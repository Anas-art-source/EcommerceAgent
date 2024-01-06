
def compare_products(query):
  """
    use this tool to compare products
  """
  from utils.llm import BasicLLM
  from utils.template import COMPARE_PRODUCT_PROMPT

  compare_product_prompt_llm = BasicLLM(COMPARE_PRODUCT_PROMPT)
  return compare_product_prompt_llm.answer(query)