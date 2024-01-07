
import re
import random

def get_related_product(query):
  """
    use this tool to generate search keywords for suggesting product to users
  """
  from utils.llm import BasicLLM
  from utils.template import RELATED_PRODUCT_PROMPT

  related_product = BasicLLM(RELATED_PRODUCT_PROMPT)
  response = related_product.answer(query)
  ## Define a regular expression pattern to match the list inside the square brackets
  pattern = r'\[([^]]+)\]'

  # Use re.search to find the match
  match = re.search(pattern, response)

  if match:
      # Extract the matched content and split it into a list
      extracted_list = match.group(1).split(', ')
      # Remove any extra quotes from the elements
      extracted_list = [element.strip("'") for element in extracted_list]
      return extracted_list
  else:
      print("No match found")



