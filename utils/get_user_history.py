

def get_user_history(user_id):
  """
    use this tool to get data of user asking question, including gender, behavioural features, and purchase history
  """
  from utils.llm import BasicLLM
  from utils.template import USER_HISTORY_PROMPT
  user_history = BasicLLM(USER_HISTORY_PROMPT)
  return user_history.answer(user_id)



