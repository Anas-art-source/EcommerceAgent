
def get_related_product(query):
  """
    use this tool to search for related products, such as complement and substitute
  """
  from utils.llm import BasicLLM
  from utils.template import RELATED_PRODUCT_PROMPT

  related_product = BasicLLM(RELATED_PRODUCT_PROMPT)
  return related_product.answer(query)
