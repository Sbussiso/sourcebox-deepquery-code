import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import DeepLake
from custom_embedding import CustomEmbeddingFunction

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the embedding function
embedding_function = CustomEmbeddingFunction(client)

def project_to_vector():
    main_directory = os.getcwd()
    repo_fetch_dir = os.path.join(main_directory, 'repofetch')
    failed_files = []

    db = DeepLake(dataset_path="./my_deeplake/", embedding=embedding_function, overwrite=True)

    for root, dirs, files in os.walk(repo_fetch_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.path.isfile(file_path):
                try:
                    loader = TextLoader(file_path)
                    documents = loader.load()
                    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                    docs = text_splitter.split_documents(documents)
                except Exception as e:
                    failed_files.append(file_path)
                    continue

                try:
                    db.add_documents(docs)
                except Exception as e:
                    failed_files.append(file_path)

    print("Document processing done!")

    for failed_file in failed_files:
        print(failed_file)

    return db

if __name__ == "__main__":
    project_to_vector()
