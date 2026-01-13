import os
from langchain.vectorstores import Qdrant
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document


# Vector Store Setup 
COLLECTION_NAME = os.getenv("VECTOR_COLLECTION_NAME", "insurance_docs")

embeddings = HuggingFaceEmbeddings(
    model_name=os.getenv(
        "EMBEDDING_MODEL_NAME",
        "sentence-transformers/all-MiniLM-L6-v2"
    )
)

vectorstore = Qdrant(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    collection_name=COLLECTION_NAME,
    embedding=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})



# RAG Node 
def rag_node(state):
    print(">>> [RAG Node] Running real document retrieval...")

    # 1️⃣ Get the last user message
    conversation = state.get("conversation", [])
    last_user_message = None

    for msg in reversed(conversation):
        if msg.__class__.__name__ == "HumanMessage":
            last_user_message = msg.content
            break

    if not last_user_message:
        print(">>> [RAG Node] No user query found for retrieval.")
        return {"retrieved_info": ""}

    print(f">>> [RAG Node] Query: {last_user_message}")

    # 2️⃣ Run retrieval
    try:
        retrieved_docs = retriever.invoke(last_user_message)
    except Exception as e:
        print(">>> [RAG Node] Retrieval error:", str(e))
        return {"retrieved_info": ""}

    # 3️⃣ Build merged retrieved document block
    merged_text = ""

    for idx, doc in enumerate(retrieved_docs, start=1):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "N/A")

        merged_text += (
            f"\n=== Retrieved Document {idx} ===\n"
            f"Source: {source}, Page: {page}\n"
            f"{doc.page_content.strip()}\n"
        )

    merged_text = merged_text.strip()

    if not merged_text:
        merged_text = "No relevant documents were found in the knowledge base."

    return {"retrieved_info": merged_text}
