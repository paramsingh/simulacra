from datetime import datetime
from typing import Optional
from scipy.spatial.distance import cosine
import numpy as np
import openai
import config

DECAY_FACTOR = 0.99

def compute_importance(description: str, model: str) -> int:
    prompt = f"""On a scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed)
and 10 is extremely poignant (e.g., a break up, college acceptance), rate the likely poignancy of the following piece of memory: {description}. Rating: <fill in>

Only give the rating as one number, nothing else.
"""
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return int(response.choices[0].message["content"])

def embed(description: str) -> np.ndarray:
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=description,
    )
    return response['data'][0]['embedding']

class Memory:
    def __init__(
            self,
            description: str,
            creation_time: int,
            last_access_time: int,
            model='gpt-3.5-turbo',
            type='memory',
            related_memories: Optional[list]=None,
        ):
        self.description = description
        self.creation_time = creation_time
        self.last_access_time = last_access_time
        self.type = type
        self.importance: int = compute_importance(description=description, model=model)
        self.embedding: np.ndarray = embed(description=description)
        self.related_memories = related_memories if related_memories else []
        print(f"new memory added! {self.description}")

    def compute_recency_score(self, decay_factor: float, current_time) -> float:
        time_difference = (current_time - self.creation_time) / 60 # time difference in hours
        return decay_factor ** time_difference

    def compute_relevance_score(self, query: str) -> float:
        memory_embedding = embed(self.description)
        query_embedding = embed(query)
        return 1 - cosine(memory_embedding, query_embedding)


if __name__ == '__main__':
    openai.api_key = config.OPENAI_API_KEY
    memory = Memory(description="i threw my mother a party today.", creation_time=datetime.now(), last_access_time=datetime.now())
    print(memory.importance)