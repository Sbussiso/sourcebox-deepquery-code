from vector import project_to_vector
def perform_query():
    db = project_to_vector()

    query = input("Query: ")
    try:
        docs = db.similarity_search(query)
        for i, doc in enumerate(docs):
            print(f"Document {i + 1}:")
            print(doc.page_content)
            print("-" * 40)
    except Exception as e:
        print(f"Error during similarity search: {e}")

if __name__ == "__main__":
    perform_query()
