from langchain.llms import OpenAI
from langchain.prompts import ChatPromptTemplate
import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

class BasicLLM():
  def __init__(self, sys_prompt):
    self.template = ChatPromptTemplate.from_messages(
    [
        ("system", sys_prompt),
        ("human", "Hello, how are you doing?"),
        ("ai", "I'm doing well, thanks!"),
        ("human", "user_input: {user_input}"),
    ]
    )
    self.llm = OpenAI(model="gpt-3.5-turbo-instruct")

  def answer(self, input):
      return self.llm.invoke(self.template.format_messages(user_input=input))
  

