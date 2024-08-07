from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import DeepLake
import os, time, sys
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define a class for the embedding function
class CustomEmbeddingFunction:
    def __init__(self, client):
        self.client = client

    def embed_documents(self, documents):
        # Convert documents to strings
        document_texts = [str(doc) for doc in documents]
        
        # Get embeddings from OpenAI
        response = self.client.embeddings.create(
            input=document_texts,
            model="text-embedding-3-small"
        )
        # Extract embeddings from response
        return [item.embedding for item in response.data]
    
    #embed queries
    def embed_query(self, query):
        # Convert query to string
        query_text = str(query)
        
        # Get embedding from OpenAI
        response = self.client.embeddings.create(
            input=[query_text],
            model="text-embedding-3-small"
        )
        # Extract embedding from response
        return response.data[0].embedding

# Initialize the embedding function
embedding_function = CustomEmbeddingFunction(client)

# Path to the directory
main_directory = os.getcwd()  # Use the current working directory as the main directory
repo_fetch_dir = os.path.join(main_directory, 'repofetch')
print(f"repo_fetch_dir: {repo_fetch_dir}")

failed_files = []  # List to store files that failed to process

for root, dirs, files in os.walk(repo_fetch_dir):
    for filename in files:
        file_path = os.path.join(root, filename)
        print(f"Processing file: {file_path}")

        # Check if the path is a file
        if os.path.isfile(file_path):
            try:
                # Load and split documents
                loader = TextLoader(file_path)
                documents = loader.load()
                text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                docs = text_splitter.split_documents(documents)
            except Exception as e:
                failed_files.append(file_path)  # Add the failed file to the list
                continue

            print(docs)

            # Initialize DeepLake with the custom embedding function
            db = DeepLake(dataset_path="./my_deeplake/", embedding=embedding_function, overwrite=True)
            db.add_documents(docs)
            print("Embeddings stored in DeepLake!")

print("\nsleeping")
time.sleep(3)
print("awake!\n")
print("test1")
query = '''if platform.system() == "Linux":
        signal.signal(signal.SIGBUS, handle_bus_error)
        root_dirs = ["/"]'''
docs = db.similarity_search(query)
print(docs)
print("Done!")

'''
print("test1")
query = "who won the world series in 1990 base ball"
docs = db.similarity_search(query)

 #do not touch
print("\n\n\n\nFiles that failed to process:")
for failed_file in failed_files:
    print(failed_file)
'''