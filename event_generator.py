import random
from datetime import datetime, timedelta

def generate_random_timestamp():
    days_ago = random.randint(0, 4)  # up to 5 days back
    random_time = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
    return random_time.isoformat()

def generate_activity_payloads(asset_id, users, products):
    activities = []

    for i in range(len(users)):
        product = random.choice(products)
        activity = {
            "asset_id": asset_id,
            "activity_name": "Product Purchase",
            "timestamp": generate_random_timestamp(),
            "identity": users[i],
            "activity_source": "web",
            "activity_params": {
                "ImageURL": product['ImageURL'],
                "productURL": product['productURL'],
                "productName": product['productName'],
                "price": product['price'],
                "currency": "$"
            }
        }
        activities.append(activity)
    
    return activities
