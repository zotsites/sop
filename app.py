import time
from lib.connect_to_pinecone import create_serverless_index, delete_serverless_index

if __name__ in "__main__":
    index_name = "test-index"
    create_serverless_index(index_name)
    time.sleep(20)
    delete_serverless_index(index_name)
