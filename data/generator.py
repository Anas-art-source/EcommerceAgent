import json
from faker import Faker
import random
import pandas as pd
from datetime import datetime, timedelta


productList = pd.read_csv('productList.csv')
productList = productList['title'].to_list()

amazon_categories = [
    "Books",
    "Electronics",
    "Home & Kitchen",
    "Toys & Games",
    "Clothing, Shoes & Jewelry",
    "Sports & Outdoors",
    "Tools & Home Improvement",
    "Beauty & Personal Care",
    "Health & Household",
    "Grocery & Gourmet Food",
    "Pet Supplies",
    "Automotive",
    "Movies & TV",
    "Music",
    "Video Games",
    "Software"
]


# Initialize Faker and seed for reproducibility
fake = Faker()
# Faker.seed(0)
# random.seed(0)


# Function to generate a random date greater than today
def generate_random_date():
    today = datetime.now()
    random_days = random.randint(1, 30)  # You can adjust the range based on your needs
    return today + timedelta(days=random_days)

# Function to generate a random order record
def generate_order():
    order_date = generate_random_date().strftime('%Y-%m-%d')
    estimated_delivery_date = (datetime.strptime(order_date, '%Y-%m-%d') + timedelta(days=random.randint(1, 10))).strftime('%Y-%m-%d')
    status_name = random.choice(['Processing', 'Shipped', 'Out for Delivery'])
    tracking_number = fake.uuid4()
    total_amount = round(random.uniform(10.0, 500.0), 2)

    product_name = random.choice(productList)
    price = round(random.uniform(5.0, 100.0), 2)
    carrier_name = fake.word()

    order = {
        "order_date": order_date,
        "estimated_delivery_date": estimated_delivery_date,
        "status_name": status_name,
        "tracking_number": tracking_number,
        "total_amount": total_amount,
        "product_name": product_name,
        "price": price,
        "carrier_name": carrier_name,
    }
    return order

# Generate 1000 random orders

def generate_record():
    return {
        'name': fake.name(),
        'customerID': fake.uuid4(),
        'address': fake.address(),
        'interested_category': random.sample(amazon_categories, random.randint(3, 5)),
        'past_purchase_category': random.sample(amazon_categories, random.randint(0, 3)),
        'past_purchase':random.sample(productList, random.randint(0, 3)),
        'delivery_pending':[generate_order() for _ in range(random.randint(0,4))]
    }

def generate_large_json_file(file_path, num_records):
    data = [generate_record() for _ in range(num_records)]
    df = pd.DataFrame(data)
    df.to_csv(file_path)

if __name__ == "__main__":
    generate_large_json_file("customerDetail.csv", 10000)