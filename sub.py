import json
import datetime
import glob
# Example subscription keys and expiration dates
SUBSCRIPTION_KEYS = {
    "key123": "2023-06-01",
    "key456": "2024-01-01"
}

def check_subscription(username):
    # Check if the user has a subscription file
    sub_file = f"{username}_sub.json"
    try:
        with open(sub_file, "r") as f:
            sub_data = json.load(f)
    except FileNotFoundError:
        # If the subscription file doesn't exist, create one with a 14-day trial
        start_date = datetime.datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
        sub_data = {
            "key": "",
            "start_date": start_date,
            "end_date": end_date,
            "status": "trial"
        }
        with open(sub_file, "w") as f:
            json.dump(sub_data, f)
    
    # Check if the subscription is still valid
    if datetime.datetime.now().strftime("%Y-%m-%d") > sub_data["end_date"]:
        # If the trial period has ended, prompt the user to enter a subscription key
        key = input("Please enter a subscription key: ")
        if key in SUBSCRIPTION_KEYS:
            end_date = SUBSCRIPTION_KEYS[key]
            sub_data["key"] = key
            sub_data["start_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
            sub_data["end_date"] = end_date
            sub_data["status"] = "valid"
        else:
            sub_data["status"] = "invalid"
        with open(sub_file, "w") as f:
            json.dump(sub_data, f)
    elif sub_data["status"] == "trial" and datetime.datetime.now().strftime("%Y-%m-%d") > sub_data["end_date"]:
        # If the trial period has ended and the user has not entered a subscription key, set the status to "invalid"
        sub_data["status"] = "invalid" 
        with open(sub_file, "w") as f:
            json.dump(sub_data, f)
    elif sub_data["status"] == "valid":
        # Check if the subscription key is still valid
        if datetime.datetime.now().strftime("%Y-%m-%d") > sub_data["end_date"]:
            # If the subscription has expired, reset it to the 14-day trial
            start_date = datetime.datetime.now().strftime("%Y-%m-%d")
            end_date = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
            sub_data["key"] = ""
            sub_data["start_date"] = start_date
            sub_data["end_date"] = end_date
            sub_data["status"] = "trial"
            with open(sub_file, "w") as f:
                json.dump(sub_data, f)
        elif sub_data["key"] not in SUBSCRIPTION_KEYS:
            # If the subscription key is not valid, set the status to "invalid"
            sub_data["status"] = "invalid"
            with open(sub_file, "w") as f:
                json.dump(sub_data, f)
    
    # Return the subscription status
    return sub_data["status"]


def write_subscriptions():
    subscriptions = {}
    for sub_file in glob.glob("*_sub.json"):
        with open(sub_file, "r") as f:
            sub_data = json.load(f)
            subscriptions[sub_file.replace("_sub.json", "")] = sub_data
    with open("subscriptions.json", "w") as f:
        json.dump(subscriptions, f)