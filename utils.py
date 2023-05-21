def print_memory_list(memories):
    for memory in memories:
            print(f"{memory.type}: {memory.creation_time}: {memory.description} | {memory.importance}")