import pandas as pd
from faker import Faker
import random

def generate_dummy_users(num_users=30000, custom_attr1=None, custom_attr2=None):
    fake = Faker()
    languages = ['Deutsch', 'English', '日本語', 'Français', 'Español']
    users = []

    for i in range(1, num_users + 1):
        user = {
            "EMAIL": f"user{i}@example.com",
            "PHONE": fake.msisdn()[-10:],  # last 10 digits
            "LANGUAGE": random.choice(languages)
        }

        if custom_attr1:
            user[custom_attr1.upper()] = f"{custom_attr1}_value_{random.randint(1, 100)}"
        if custom_attr2:
            user[custom_attr2.upper()] = f"{custom_attr2}_value_{random.randint(1, 100)}"

        users.append(user)

    df = pd.DataFrame(users)
    df.to_csv("dummy_users.csv", index=False)
    print(f"{num_users} dummy users saved to dummy_users.csv ✅")

# Example test
if __name__ == "__main__":
    generate_dummy_users(
        num_users=30000,
        custom_attr1="CustomerType",
        custom_attr2="SignupSource"
    )
