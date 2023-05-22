import sys
from typing import List
from memory import Memory
from utils import print_memory_list
import numpy as np
from datetime import datetime
import openai
import config
import pickle
import os

class Agent:
    def __init__(self, name, description, model='gpt-3.5-turbo', memory_decay_factor: int=0.99):
        self.name: str = name
        self.description: str = description
        self.memory_stream: List[Memory] = []
        self.memory_decay_factor: int = memory_decay_factor
        self.model = model

    def add_memory(self, description, current_time):
        memory = Memory(description=description, creation_time=current_time, last_access_time=current_time, model=self.model)
        self.memory_stream.append(memory)

    def retrieve_memories(self, query: str, current_time, max_count: int=10):
        scores = []
        for memory in self.memory_stream:
            recency_score = memory.compute_recency_score(self.memory_decay_factor, current_time)
            relevance_score = memory.compute_relevance_score(query)
            score = 1.0 * recency_score + 1.0 * memory.importance + 1.0 * relevance_score
            scores.append(score)

        top_indices = np.argsort(scores)[-max_count:]
        return [self.memory_stream[i] for i in top_indices]

    def should_reflect(self):
        recent_memories = sorted(self.memory_stream, key=lambda x: x.creation_time, reverse=True)
        recent_memories = recent_memories[:5]  # limit to last 100 memories
        sum_importance = sum([mem.importance for mem in recent_memories if mem.type == 'memory'])
        return sum_importance > 18

    def reflect(self, current_time):
        """
        Generate a reflection based on the past few memories.
        """
        recent_memories = sorted(self.memory_stream, key=lambda x: x.creation_time, reverse=True)
        recent_memories = recent_memories[:100]  # limit to last 100 memories
        context = "\n".join([f"{i+1}. {mem.description}" for i, mem in enumerate(recent_memories)])

        # Construct the query to the model for generating questions
        question_prompt = f"""{context}

Given only the information above, what are 3 most salient high-level questions that {self.name} should reflect on?

Only reply with the questions (each in a new line), nothing else. Do not number or bullet the list.
"""

        # Query the model for questions
        print("reflecting...")
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "user", "content": question_prompt}
            ],
        )
        questions = response.choices[0].message["content"].strip().split("\n")
        questions = [q.strip() for q in questions if q.strip() != ""]
        for question in questions:
            print("reflecting on question: ", question)
            # Retrieve relevant memories for each question
            relevant_memories = self.retrieve_memories(question, 5)

            # Format the relevant memories into a string context for the insight prompt
            context = "\n".join([f"{i+1}. {mem.description}" for i, mem in enumerate(relevant_memories)])

            # Construct the query to the model for generating insights
            insight_prompt = f"""
Context: {context}

What high-level insight about the question can {self.name} infer from the above context?

Only reply with the insight, nothing else. The insight should be in the format "{self.name} should/can/needs to/should not/cannot/does not need to/does not have to <insight>".

Question: {question}
"""

            # Query the model for insight
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": insight_prompt},
                ],
            )
            insight = response.choices[0].message["content"].strip()

            # Create and store reflection
            reflection = Memory(description=insight, creation_time=current_time, last_access_time=current_time, model=self.model, type="reflection")
            print(f"Reflection: {reflection.description}")
            self.memory_stream.append(reflection)

    def create_daily_plan(self, current_time):
        """
        Create a high-level plan for the agent's day, based on the agent's description
        and recent experiences.
        """
        # Retrieve recent memories for the agent
        recent_memories = sorted(self.memory_stream, key=lambda x: x.creation_time, reverse=True)
        recent_memories = recent_memories[:10]
        context = "\n".join([f"{i+1}. {mem.description}" for i, mem in enumerate(recent_memories)])

        # Format the prompt for creating the daily plan
        prompt = f"""
Name: {self.name}
Description: {self.description}
Recent experiences:
{context}
Devise a plan for {self.name} in broad strokes for their day. Only reply with the plan with each task in one line, nothing else.

Use this format (7: do x 8: do y ... 21: Go to sleep). Make sure the numbers are the hours of the day from 0 - 24 (not 0-12)

Start with current hour of day: {current_time % 24}
"""
        # Generate the daily plan
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )

        # Extract the plan from the model's response
        plan = response.choices[0].message["content"].strip()

        # Create a Plan memory and store it in the agent's memory_stream
        plan_memory = Memory(description=plan, type='plan', creation_time=current_time, last_access_time=current_time)
        self.memory_stream.append(plan_memory)
        self.todays_plan = plan_memory

        return plan

    def execute_next(self, current_time):
        recent_memories = sorted(self.memory_stream, key=lambda x: x.creation_time, reverse=True)
        recent_memories = recent_memories[:10]
        context = "\n".join([f"{i+1}. {mem.description}" for i, mem in enumerate(recent_memories)])

        prompt = f"""
Name: {self.name}
Description: {self.description}
Recent experiences:
{context}
Current hour of day: {current_time % 24}
Today's plan with tasks for each hour of day:
{self.todays_plan.description}

What does {self.name} do next at the current hour of day, based on today's plan? Example output: {self.name} does X.

Do not mention the current hour of day or the plan in your response. Only say something like "{self.name} does X".
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        next_task = response.choices[0].message["content"].strip()
        self.memory_stream.append(Memory(description=next_task, creation_time=current_time, last_access_time=current_time))
        self.print_memory_stream()

    def print_memory_stream(self):
        print_memory_list(self.memory_stream)

if __name__ == "__main__":
    openai.api_key = config.OPENAI_API_KEY
    # Creating the agent
    if not os.path.exists("data/klaus_no_reflections.pickle"):
        klaus = Agent("Klaus Mueller", "A passionate researcher")

        # Adding memories
        klaus.add_memory("Klaus Mueller is reading a book on gentrification")
        klaus.add_memory("Klaus Mueller is conversing with a librarian about his research project")
        klaus.add_memory("Klaus Mueller is discussing gentrification with Maria Lopez")
        klaus.add_memory("Klaus Mueller is writing a research paper")
        klaus.add_memory("Klaus Mueller attended a seminar on urban planning")
        klaus.add_memory("Klaus Mueller met with his research advisor to discuss his project")
        klaus.add_memory("Klaus Mueller visited a gentrified neighborhood for field research")
        klaus.add_memory("Klaus Mueller interviewed residents about the effects of gentrification")
        klaus.add_memory("Klaus Mueller submitted his research paper for a conference")
        klaus.add_memory("Klaus Mueller is planning to write a book based on his research")
        with open("data/klaus_no_reflections.pickle", "wb") as f:
            pickle.dump(klaus, f)

        klaus.print_memory_stream()
    else:
        print("using pickled object")
        with open("data/klaus_no_reflections.pickle", "rb") as f:
            klaus = pickle.load(f)
        klaus.print_memory_stream()
        klaus.create_daily_plan()
        klaus.print_memory_stream()
        sys.exit(0)

    # Making the agent reflect
    klaus.reflect()
    klaus.print_memory_stream()
    with open("data/klaus_with_reflections.pickle", "wb") as f:
        pickle.dump(klaus, f)