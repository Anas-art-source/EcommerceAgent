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
import time
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
        # self.print_response(responses)
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
        time.sleep(5)
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
  
  def print_response(self,response_string):
    # Define the regular expression pattern to extract information
    pattern_thought = r'Thought: ([^"]+)\n'
    pattern_action = r'Action: ([^"]+)\n'
    pattern_action_input = r'Action Input: ([^"]+)'


    # Find matches using the pattern
    match_thought = re.search(pattern_thought, response_string)
    match_action = re.search(pattern_action, response_string)
    match_action_input = re.search(pattern_action_input, response_string)
    if match_thought:
        thought = match_thought.group()
        # Print colored text
        print(colored("Thought: ", 'green', attrs=["reverse", "blink"]), end="", flush=True)
        print(thought)

    # Find matches using the pattern

    if match_action:
        action = match_action.group()
        # Print colored text
        print(colored("Action: ", 'red', attrs=["reverse", "blink"]), end="", flush=True)
        print(action)

    # Find matches using the pattern

    if match_action_input:
        action_input = match_action_input.group()
        # Print colored text
        print(colored("Action Input: ", 'red',attrs=["reverse", "blink"]), end="", flush=True)
        print(action_input)

  def _sys_prompt_generator(self):
    data_string = '[{"row_number": "84", "name": "Rhonda Larsen", "customerID": "eacf35c9-bd28-4ec6-bf5f-71a8d889be29", "address": "8035 Jason Dale Suite 661\\nLake Kelseyfurt, TN 56120", "interested_category": ["Beauty & Personal Care", "Toys & Games", "Tools & Home Improvement"], "past_purchase_category": ["Electronics", "Pet Supplies", "Books"], "past_purchase": [], "delivery_pending": [{"order_date": "2024-01-11", "estimated_delivery_date": "2024-01-15", "status_name": "Processing", "tracking_number": "d59c4ad7-acfb-4326-a8b8-8c7c4810d003", "total_amount": 483.28, "product_name": "Yale Assure Lock SL, Wi-Fi Smart Lock with Norwood Lever - Works with the Yale Access App, Amazon Alexa, Google Assistant,...", "price": 18.7, "carrier_name": "treat"}, {"order_date": "2024-01-21", "estimated_delivery_date": "2024-01-29", "status_name": "Processing", "tracking_number": "c5456e45-104c-4089-be20-867da04983e8", "total_amount": 445.55, "product_name": "Flash Furniture High Back Traditional Tufted Black LeatherSoft Executive Ergonomic Office Chair with Oversized Headrest & ...", "price": 31.2, "carrier_name": "use"}}]}]'

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

      Example Session:

User Question: userid (eacf35c9-bd28-4ec6-bf5f-71a8d889be29): I need to find product that will interest me?

Thought: User need to look for product is according to his interest and preferences. Therefore, I need to first look at users history to know about his interested categories and past purchases. Then I will generate search keywords related to customer past purchase. Finally, I will search for these products using keywords generated.
Action: get_user_history
Action Input: eacf35c9-bd28-4ec6-bf5f-71a8d889be29

Observation: user data will be provided

Though: User, Rhonda, seems to be interested in 'Beauty & Personal Care', 'Toys & Games', 'Tools & Home Improvement', 'Electronics', 'Pet Supplies', and 'Books'. Therefore, I should pick any 1 category from above and use the get_related_product tool to generate a search query. Then I will use a search query to look for products.
Action: get_related_product 
Action Input: Beauty & Personal Care

Observation: list of search keywords will be provided

Thought: Now, I know the search keywords to find product that will interest customer. I will use search_product to find relevant products.
Action: search_product
Action Input: one of the search keywords

Observation: Product details will be provided


Thought: I now know the final answer. I should use respond_to_human tool to give my final answer.
Action: respond_to_human
Action Input: respond based on the observation

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

# print(tools_repo)

tools_description = "\n".join([f"{x['tool_name']}: {x['description']} \n" for x in tools_repo])

a = Agent('You are the helpful bot with the name DiscoverDaraz', tools=tools_repo,tools_description=tools_description)

while True:
   print("Your Query: ", end="")
   query = input()
   query = "userID (eacf35c9-bd28-4ec6-bf5f-71a8d889be29): " + query
   a.agent_iterator(query)
   print("-"*100)
   print(" ")
