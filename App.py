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
            model='gpt-4',
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

Observation: {data_string}

Though: User, Rhonda, seems to be interested in 'Beauty & Personal Care', 'Toys & Games', 'Tools & Home Improvement', 'Electronics', 'Pet Supplies', and 'Books'. Therefore, I should pick any 1 category from above and use the get_related_product tool to generate a search query. Then I will use a search query to look for products.
Action: get_related_product 
Action Input: Beauty & Personal Care

Observation: [‘Haircare routine’, “Natural beauty remedies”, “Skincare products”]

Thought: Now, I know the search keywords to find product that will interest customer. I will use search_product to find relevant products.
Action: search_product
Action Input: Haircare routine

Observation: following are the products Rhonda might me interested in:
Product 1:
Title: amika dream routine overnight hydrating hair mask, 100ml
Description: (empty)
Feature Bullets: (empty)
Price:
Symbol: $
Currency: USD
Current Price: 32
Discounted: false
Before Price: 32
Savings Amount: 0
Savings Percent: 0

Title: PURA D'OR Hair Thinning Therapy Biotin Shampoo and Conditioner Set, CLINICALLY TESTED Proven Results, DHT Blocker Hair Thickening Products For Women & Men, Natural Routine, Color Safe, 16oz x2
Description: (empty)
Feature Bullets:
INCREASED VOLUME, REDUCED THINNING: ...
ORGANIC INGREDIENT BASED SHAMPOO: ...
PROTECT & STRENGTHEN YOUR HAIR: ...
IMPROVED HAIR APPEARANCE: ...
THE PURA D'OR PROMISE: Healthy hair for happy customers. We offer a 100% Satisfaction Guarantee. If you are unsatisfied with our all natural shampoo and conditioner, let us know and we will give you a FULL refund.
Price:
Symbol: $
Currency: USD
Current Price: 24.69
Discounted: false
Before Price: 24.69
Savings Amount: 0
Savings Percent: 0
Product 2:
Title: OGX Thick & Full + Biotin & Collagen Shampoo & Conditioner Set, (packaging may vary), Purple, 13 Fl Oz (Pack of 2)
Description: Plump up the volume in thin hair with the OGX Thick & Full + Biotin & Collagen Hair Volumizing Shampoo and Conditioner...
Feature Bullets:
PLUMP UP THE VOLUME: ...
THICKER, FULLER, HEALTHIER: ...
HAIR CARE INSPIRED BY NATURE: ...
ALL-AROUND SENSORY EXPERIENCE: ...
BEAUTY PURE & SIMPLE: For best results, use this OGX Biotin & Collagen hair care collection to help infuse nutrients into every strand.
Price:
Symbol: $
Currency: USD
Current Price: 10.9
Discounted: true
Before Price: 50
Savings Amount: 39.1
Savings Percent: 78.2


Thought: I now know the final answer. I should use respond_to_human tool to give my final answer.
Action: respond_to_human
Action Input: Title: amika dream routine overnight hydrating hair mask, 100ml

Unfortunately, the provided information for the amika dream routine overnight hydrating hair mask is quite limited, as the description and feature bullets are empty. However, it is priced at $32 USD, with no apparent discount, as both the discounted and savings fields indicate false values. Comparatively, we have more detailed information about the other two products, allowing for a more comprehensive analysis.

Title: PURA D'OR Hair Thinning Therapy Biotin Shampoo and Conditioner Set, CLINICALLY TESTED Proven Results, DHT Blocker Hair Thickening Products For Women & Men, Natural Routine, Color Safe, 16oz x2

The PURA D'OR Hair Thinning Therapy Biotin Shampoo and Conditioner Set seems to be a well-rounded solution for increased volume and reduced thinning, with organic ingredients enhancing its appeal. Priced at $24.69 USD, it offers a competitive option compared to the amika product. Additionally, the product emphasizes a 100% Satisfaction Guarantee, showing the brand's commitment to customer satisfaction.

Product 2: OGX Thick & Full + Biotin & Collagen Shampoo & Conditioner Set, (packaging may vary), Purple, 13 Fl Oz (Pack of 2)

The OGX Thick & Full + Biotin & Collagen Shampoo & Conditioner Set, priced at a discounted $10.9 USD from an original price of $50, provides a significant cost advantage. It focuses on volume enhancement and healthier hair, with a unique emphasis on a sensory experience. This product seems to be a budget-friendly yet effective choice, especially given the substantial 78.2% savings.

In summary, while the amika product lacks detailed information, the PURA D'OR set offers a natural solution with a satisfaction guarantee at $24.69. On the other hand, the OGX set stands out for its budget-friendly pricing, discounted at $10.9 with a remarkable 78.2% savings, making it an attractive option for those looking for an economical yet quality hair care solution.



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
