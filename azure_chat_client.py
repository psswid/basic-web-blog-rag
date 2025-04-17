import os
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI

class AzureChatClient:
    def __init__(self):
        deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        if not deployment_name:
            raise ValueError("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME environment variable is not set.")
        self.client = AzureChatOpenAI(deployment_name=deployment_name)

    def ask(self, prompt: str) -> str:
        message = HumanMessage(role="user", content=prompt)
        return self.client.invoke([message])
