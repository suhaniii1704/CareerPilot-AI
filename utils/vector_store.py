from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from utils.embeddings import load_embedding_model


def create_vector_store(resume_text):
    """
    Creates a FAISS vector database from the resume text.
    """

    # Split the resume into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_text(resume_text)

    print("Resume length:", len(resume_text))
    print("Chunks created:", len(chunks))
    print(chunks[:2])

    # Load embedding model
    embeddings = load_embedding_model()

    # Create FAISS vector store
    vector_store = FAISS.from_texts(
        texts=chunks,
        embedding=embeddings
    )

    return vector_store