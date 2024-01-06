
def get_recipe_search_keyword(query):
  """
    use this tool to search to generate keywords for ingredient in the recipe
  """
  from utils.llm import BasicLLM
  from utils.template import RECIPE_KEYWORD_PROMPT
  recipe_search_keywords = BasicLLM(RECIPE_KEYWORD_PROMPT)

  return recipe_search_keywords.answer(query)


print(get_recipe_search_keyword("dsfasf"))
