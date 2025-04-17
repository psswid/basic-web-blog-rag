from blog_fetcher import BlogFetcher
from azure_chat_client import AzureChatClient
from qdrant_hybrid_store import QdrantHybridStore
from langchain_core.documents import Document
from BlogRAG import BlogRAG
import json

if __name__ == "__main__":
    # Fetch AI blog URLs
    blog_fetcher = BlogFetcher()
    ai_urls = blog_fetcher.fetch_ai_blog_urls()

    # Fetch and parse blog posts, then store in Qdrant
    blog_posts = []
    for url in ai_urls:
        # You need to implement fetch_blog_post_details in BlogFetcher
        post_data = blog_fetcher.fetch_blog_post_details(url)  # returns dict with title, body, authors, tags, date
        doc = Document(
            page_content=post_data["body"],
            metadata={
                "title": post_data["title"],
                "authors": post_data["authors"],
                "tags": post_data["tags"],
                "date": post_data["date"],
                "url": url
            }
        )
        blog_posts.append(doc)

    qdrant_store = QdrantHybridStore()
    qdrant_store.create_store(blog_posts)
    print("Stored blog posts in Qdrant.")

    # RAG: Answer all questions from questions.json and save to answers.json
    blog_rag = BlogRAG(qdrant_store=qdrant_store)
    with open("questions.json", "r") as f:
        questions = json.load(f)
    with open("answers.json", "r") as f:
        try:
            answers = json.load(f)
        except json.JSONDecodeError:
            answers = {}
    for qid, question in questions.items():
        print(f"Answering: {question}")
        answer = blog_rag.answer_blog_question(question)
        # Ensure answer is a string (extract .content if it's an AIMessage)
        if hasattr(answer, "content"):
            answers[qid] = answer.content
        else:
            answers[qid] = str(answer)
    with open("answers.json", "w") as f:
        json.dump(answers, f, indent=4)
    print("All answers saved to answers.json.")

