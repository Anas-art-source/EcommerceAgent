import requests
import re

def search_product(search_keyword):
    """
    use this tool to search product in ecommerce platform. 
    Argument: 
        search_keyword: one search keyword
    """
    url = f'http://localhost:3000/search/{search_keyword}'
    response = requests.get(url)
    if response.status_code == 200:
        # Print the content of the response
        return response.text
    else:
        print("No match found")
 
 