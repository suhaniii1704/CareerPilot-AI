from langchain_google_genai import GoogleGenerativeAIEmbeddings

from utils.config import API_KEY


def load_embedding_model():
    """
    Load Google's embedding model.
    """

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=API_KEY
    )

    return embeddings