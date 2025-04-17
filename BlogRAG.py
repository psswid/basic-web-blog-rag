from qdrant_hybrid_store import QdrantHybridStore
from azure_chat_client import AzureChatClient

class BlogRAG:
    def __init__(self, qdrant_store=None, collection_name="my_documents", location=":memory:"):
        if qdrant_store is not None:
            self.qdrant_store = qdrant_store
        else:
            self.qdrant_store = QdrantHybridStore(collection_name=collection_name, location=location)
        self.llm_client = AzureChatClient()

    def answer_blog_question(self, question: str, top_k: int = 3) -> str:
        """
        Retrieve relevant blog docs from Qdrant and answer the question using LLM.
        """
        # Retrieve relevant docs
        docs = self.qdrant_store.similarity_search(question)
        if not docs:
            return "No relevant blog content found."
        # Prepare context from docs
        context = "\n---\n".join([
            f"Title: {doc.metadata.get('title', '')}\nDate: {doc.metadata.get('date', '')}\nAuthors: {', '.join(doc.metadata.get('authors', []))}\nTags: {', '.join(doc.metadata.get('tags', []))}\nContent: {doc.page_content[:1000]}..."
            for doc in docs[:top_k]
        ])
        # Compose prompt
        prompt = (
            f"You are an assistant with access to the following blog articles:\n{context}\n\n"
            f"Based on the above, answer the following question as accurately as possible.\nQuestion: {question}"
        )
        # Get answer from LLM
        answer = self.llm_client.ask(prompt)
        return answer
