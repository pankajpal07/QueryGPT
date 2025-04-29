from mem0 import Memory
import os
from indexing import initiate_indexing
from openai import OpenAI

def get_memory_client():
    config = {
        "version": "v1.1",
        "embedder": {
            "provider": "gemini",
            "config": {
                "api_key": os.getenv('API_KEY'),
                "model": "gemini-embedding-exp-03-07"
            },
        },
        "llm": {
            "provider": "gemini",
            "config": {
                "api_key": os.getenv('API_KEY'),
                "model": os.getenv('MODEL')
            }
        },
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "api_key": os.getenv('QDRANT_API_KEY'),
                "host": os.getenv('QDRANT_HOST'),
                "port": 6333
            },
        },
        "graph_store": {
            "provider": "neo4j",
            "config": {
                "url": os.getenv('NEO4J_URL'),
                "username": os.getenv('NEO4J_USERNAME'),
                "password": os.getenv('NEO4J_PASSWORD')
            },
        },
    }

    os.environ["MEM0_API_KEY"] = os.getenv('MEM0_API_KEY')

    mem_client = Memory.from_config(config)
    print("Memory client initialized successfully.")
    return mem_client

def get_chat_client():
    chat_client = OpenAI(
        api_key=os.getenv("API_KEY"),
        base_url=os.getenv("BASE_URL")
    )

    return chat_client
    
def main():

    print("Initializing memory client...")
    mem_client = get_memory_client()
    chat_client = get_chat_client()
    print("Initiating Indexing...")

    initiate_indexing(chat_client, mem_client)

    # system_prompt = """
    # You are QueryGPT, a data-focused assistant designed to answer questions using structured data and domain-specific documents.
    # Only answer questions based on the provided knowledge or documents. If the answer is not found, respond with: `The information is not available in the current data.`
    # Do not make assumptions or create content. You may receive user queries in natural language. Interpret them accurately and match them to relevant fields or content.
    # Do not change the meaning of the query. Return responses in markdown format. Use bullet points for lists. If asked for data summaries, use structured headings.

    # Rules:
    #  - Always respond in markdown format.
    #  - Do not speculate, assume or hallucinate.
    #  - If the answer is not found, respond with: `The information is not available in the current data.`
    # """
    # print("Hello from querygpt!")


if __name__ == "__main__":
    main()
