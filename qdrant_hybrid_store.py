from langchain_openai import AzureOpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from langchain_core.documents import Document

class QdrantHybridStore:
    def __init__(self, collection_name="my_documents", location=":memory:"):
        self.embeddings = AzureOpenAIEmbeddings(model="text-embedding-3-large", azure_deployment="embedding")
        self.sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        self.collection_name = collection_name
        self.location = location
        self.qdrant = None

    def create_store(self, documents: list[Document]):
        self.qdrant = QdrantVectorStore.from_documents(
            documents,
            embedding=self.embeddings,
            sparse_embedding=self.sparse_embeddings,
            location=self.location,
            collection_name=self.collection_name,
            retrieval_mode=RetrievalMode.HYBRID,
        )

    def similarity_search(self, query: str):
        if not self.qdrant:
            raise ValueError("Qdrant store not initialized. Call create_store first.")
        return self.qdrant.similarity_search(query)
