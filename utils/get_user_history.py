import requests
import re


def get_user_history(user_id):
  """
    use this tool to get data of user asking question, including gender, behavioural features, and purchase history
  """

  # Your input string
  input_string = user_id

  # Define a regular expression pattern to match the userId inside the round brackets
  pattern = r'\(([^)]+)\)'

  # Use re.search to find the match
  match = re.search(pattern, input_string)

  if match:
      userId = match.group(1)
      url = f'http://localhost:3000/customerDetail/{userId}'
      response = requests.get(url)
      if response.status_code == 200:
          # Print the content of the response
          return response.text
      else:
      # Print an error message if the request was unsuccessful
        print(f"Error: {response.status_code} - {response.text}")
  else:
      url = f'http://localhost:3000/customerDetail/{input_string}'
      response = requests.get(url)
      if response.status_code == 200:
          # Print the content of the response
          return response.text
      else:
      # Print an error message if the request was unsuccessful
        print(f"Error: {response.status_code} - {response.text}")

 
 




