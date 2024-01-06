import os
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
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
        print(" ")
        # prompt = f"""
        # user's input: {self.user_prompt}
        # context: redmi note 6 has bigger screen than oppo and it is also cheaper
        # """
        # print(prompt)

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
    output_format = """
          Output could be Thought, Action, Action_input, Final_answer
          Thought is what you understand from user_query and context
          Action is what action you want to take from given tools
          Action_input is what argument you want to give to tool mention in action above.
          Final_answer is your final answer for user_query.

          Dont use your prior knowledge in assuming Observation
          You are the part of complex system, which is broken down to multi-steps. There is no limit of steps. At one step, you can only output either Thought + Action + Action_input, Observation, Final_answer
    """
    example = r"""
        Example Session 1:
        user's input: user 123PK: Recommend me some product?

        Thought: I should look at user history to understand his behaviour, interested product and interested categories
        Action: get_user_history[123PK]

        PAUSE
        you will be provided with observation from the action you took above. On the basis of observation, you will think (Thought) and either take action or emit Answer

        Example Session 2:
        user's input: user  874BD: I am planning of cooking biryani this weekend. Suggest me products for it?

        Thought: Biryani is tradition rice-based dish from subcontinent. I need to look for biryani recipe and suggest it ingredient.
        Action: get_reciple_search_keyword: recipe of biryani

        PAUSE
        you will be provided with observation from the action you took above. On the basis of observation, you will think (Thought) and either take action or emit Answer

        Example Session 3:
        user's input: user  213BD: Hi, help me find a product.

        Thought: Since the user is not asking for any specific requirement, I dont need to use any tool. I can give final answer.
        Answer: Sure, what are you looking for?

        Example Session 4:
        user's input: user  213BD: I need to know the difference between Almond and Pistacho.
        context: Both are dry fruits, but almonds are more cheaper and pistacho are more healthier

        Thought: Since, the context provided to me is relevant to answer user, I am going to give Answer
        Answer: Both almonds and pistachios are nutritious nuts, each with its unique set of qualities. Almonds are generally more cost-effective, making them an economical choice, while pistachios are renowned for their health benefits, being considered a nutrient-dense option. It's important to strike a balance between budget considerations and health priorities when deciding between these two wholesome snacks.

      """
    prompt = f"""
        Answer the following questions and obey the following commands as best you can.

      You have access to the following tools:
      {self.tools_description if self.tools_description else "No tools available"}

      You will receive a message from the human, then you should start a loop and do one of two things:

      Option 1: You use a tool to answer the question.

      For this, you should use the following format:

      Thought: You should always think about what to do
      Action: The action to take, should be one of[{", ".join([x['tool_name'] for x in self.tools])}]
      Action Input: The input to the action, to be sent to the tool
      After this, the human will respond with an observation, and you will continue.

      Option 2: You respond to the human.

      For this, you should use the following format:

      Action: Response To Human, should be respond_to_human
      Action Input: Your response to the human, summarizing what you did and what you learned


      Begin!
    """

    return prompt
  


tools_repo = []

tools=[get_recipe_search_keyword, get_related_product, get_user_history, compare_products,respond_to_human]
for tool in tools:
  tools_repo.append({
      'tool_name': tool.__name__,
      'callable': tool,
      'description': tool.__doc__
  })

print(tools_repo)

tools_description = "\n".join([f"{x['tool_name']}: {x['description']} \n" for x in tools_repo])

a = Agent('You are the helpful bot with the name DiscoverDaraz', tools=tools_repo,tools_description=tools_description)

a.agent_iterator("userID (231PK): Compare Nikon DSLR and AQWA DSLR")