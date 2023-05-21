from config import OPENAI_API_KEY
from agent import Agent
import openai
import pickle
import os


def main():
    if not os.path.exists("data/robinson.pickle"):
        robinson = Agent(
            name="Robinson Crusoe",
            description="Robinson Crusoe, a skilled mariner, has been unexpectedly cast away on a deserted island due to a shipwreck. " +
                        "Despite the initial shock and fear, Crusoe is determined to survive and escape. " +
                        "He is resourceful and has started thinking about ways to utilize the limited resources around him to create a makeshift shelter and find food. " +
                        "Crusoe knows that he must also maintain his resilience in order to withstand the physical and emotional challenges that lie ahead.",
        )
        robinson.add_memory("Robinson Crusoe awakes on the shore of a deserted island after surviving a shipwreck.")
        robinson.add_memory("Robinson Crusoe explores the island, finding a source of fresh water.")
        robinson.add_memory("Robinson Crusoe discovers a grove of fruit trees, providing a source of food.")
        robinson.add_memory("Robinson Crusoe builds a makeshift shelter from branches and leaves.")
        robinson.add_memory("Robinson Crusoe finds the wreckage of his ship washed up on the shore and salvages some tools and supplies.")
        robinson.add_memory("Robinson Crusoe carves a large 'HELP' sign into the beach in the hope of attracting the attention of passing ships.")
        robinson.add_memory("Robinson Crusoe makes a fire by striking stones together to create sparks.")
        with open("data/robinson.pickle", "wb") as f:
            pickle.dump(robinson, f)
    else:
        print("using pickled object")
        with open("data/robinson.pickle", "rb") as f:
            robinson = pickle.load(f)

    robinson.print_memory_stream()
    time = 7
    robinson.create_daily_plan(time)
    for _ in range(10):
        if robinson.should_reflect():
            robinson.reflect()
        robinson.execute_next(time)
        time += 1



if __name__ == '__main__':
    openai.api_key = OPENAI_API_KEY
    main()