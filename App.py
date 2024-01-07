import os
import openai
from termcolor import colored
import json
from typing import List
import re
from utils.get_recipe_keyword import get_recipe_search_keyword
from utils.get_related_product import get_related_product
from utils.get_user_history import get_user_history
from utils.compare_product import compare_products
from utils.respond_to_human import respond_to_human
from utils.search_product import search_product

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')


class Agent():
  def __init__(self, sys_prompt, tools, tools_description):
    self.sys_prompt = sys_prompt
    self.tools = tools
    self.tools_description = tools_description
    self.output = ""
    self.llm = self.llm()
    self.user_prompt = ""
    self.action_context = ""
    self.function_call_context = ""

  def llm(self):
    #define your LLM
    # print(self._sys_prompt_generator())
     pass
    # return BasicLLM(self._sys_prompt_generator())

  def _answer(self, prompt):
    return self.llm.answer(prompt)


  def agent_iterator(self, user_prompt):
    messages  = [
          { "role": "system", "content":  self._sys_prompt_generator()},
          { "role": "user", "content": f"user question: {user_prompt}"},
        ]
    i = 0
    while True:
        i+= 1
        output = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            temperature=0.3,
            stream=False,
            messages=messages,

        )

        #process each chunk
        responses  = output['choices'][0]['message']['content']
        print(colored(responses, 'green'), end="", flush=True)

        callable_name, argument = self._callable_function(responses)

        if callable_name == "response to human" or callable_name == "respond_to_human" or callable_name == 'respond to human':
          respond_to_human(argument)
          break
        answer = [x for x in self.tools if x['tool_name'] == callable_name][0]['callable'](argument)
        self.function_call_context = f"{answer}"
        print(colored(f"\nObservation: {self.function_call_context}", 'blue'), end="", flush=True)
        messages.extend([
              { "role": "system", "content":  responses},
              {"role": "user", "content": f"Observation: {self.function_call_context}" },
            ])

        print(" ")




  def _finish(self, input_string):
      pattern = r"Final_Answer"
      # Check if the pattern is found in the input string
      result = bool(re.search(pattern, input_string))
      return result

  def _callable_function(self, input_string):
      # Define regex patterns for Action and Action_input
      pattern = re.compile(r'Action Input:\s*(.*)', re.DOTALL)

      action_pattern = r"Action: (.+)"
      action_input_pattern = re.compile(r'Action Input:\s*(.*)', re.DOTALL)

      # Search for patterns in the input string
      action_match = re.search(action_pattern, input_string)
      action_input_match = action_input_pattern.search(input_string)
      # Extract values if patterns are found
      action = action_match.group(1) if action_match else None
      action_input = action_input_match.group(1).strip() if action_input_match else None
      return action.lower(), action_input.lower()

  def _action(self, input_string):
    pattern = r"PAUSE"
    # Check if the pattern is found in the input string
    result = bool(re.search(pattern, input_string))
    return result

  def _sys_prompt_generator(self):
    prompt = f"""
      Answer the following questions and obey the following commands as best you can.

      You have access to the following tools:
      {self.tools_description if self.tools_description else "No tools available"}

      You will receive a message from the human, then you should start a loop and do one of two things:

      Option 1: You use a tool to answer the question. You can use tool N number of times.

      For this, you should use the following format:

      Thought: You should always think about what to do
      Action: The action to take, should be one of [{", ".join([x['tool_name'] for x in self.tools])}]
      Action Input: The input to the action, to be sent to the tool
      After this, the human will respond with an observation, and you will continue.

      Option 2: You respond to the human.

      For this, you should use the following format:

      Action: Response To Human, should be respond_to_human
      Action Input: Your response to the human, summarizing what you did and what you learned


      Action should be the name of tool only such as [{", ".join([x['tool_name'] for x in self.tools])}]

      Begin!
    """

    return prompt
  


tools_repo = []

tools=[get_recipe_search_keyword, get_related_product, get_user_history, compare_products,respond_to_human,search_product]
for tool in tools:
  tools_repo.append({
      'tool_name': tool.__name__,
      'callable': tool,
      'description': tool.__doc__
  })

print(tools_repo)

tools_description = "\n".join([f"{x['tool_name']}: {x['description']} \n" for x in tools_repo])

a = Agent('You are the helpful bot with the name DiscoverDaraz', tools=tools_repo,tools_description=tools_description)

while True:
   print("Your Query: ", end="")
   query = input()
   query = "userID (eacf35c9-bd28-4ec6-bf5f-71a8d889be29): " + query
   a.agent_iterator(query)
   print("-"*100)
   print(" ")
