import requests
import re
import json
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
        if len(response.text) > 0:
            response = json.loads(response.text)
            products = []
            for product in response:
                products.append({
                    "name": product['title'],
                    'description': product['description'],
                    "feature_bullets": product['feature_bullets'],
                    'current_price': product['price']['current_price'],
                    'discount': product['price']['savings_amount']
                })
            return products
    else:
        print("No match found")
 
 