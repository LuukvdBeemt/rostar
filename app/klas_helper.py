# Usage: 
# Run 'klas_helper add <FRIENDLY_NAME> <KLAS_NAME>' to add a klas to the JSON file
# Run 'klas_helper remove <FRIENDLY_NAME>' to remove a klas to the JSON file
# Run 'klas_helper list' to list all klasses inside the JSON file

import json
import os
from helpers import *

# File to store the klas information
klas_file = "/data/klassen.json"

# Function to load klas data from JSON file
def load_klas_data():
    if os.path.exists(klas_file):
        with open(klas_file, "r") as f:
            return json.load(f)
    else:
        return {}

# Function to save klas data to JSON file
def save_klas_data(data):
    with open(klas_file, "w") as f:
        json.dump(data, f, indent=4)

# Function to add a new klas
def add_klas(friendly_name, klas_name):
    data = load_klas_data()
    klas_id = get_class_id(klas_name)
    data[friendly_name] = klas_name, klas_id
    save_klas_data(data)

# Function to remove a klas
def remove_klas(friendly_name):
    data = load_klas_data()
    if friendly_name in data:
        del data[friendly_name]
        save_klas_data(data)
    else:
        print(f"No klas found with the friendly name: {friendly_name}")

# Function to list all klasses
def list_klas():
    data = load_klas_data()
    for friendly_name, klas_name_id in data.items():
        print(f"Friendly Name: {friendly_name}, Klas Name: {klas_name_id[0]}")
        
# Function to get the klas id from rostareduflex
def get_class_id(klas_name):
    sessionCookies = login(os.environ['ROSTAR_USER'], os.environ['ROSTAR_PASS'])
    idList = fetch_klas_mapping(sessionCookies)
    if klas_name in idList:
        return idList[klas_name]
    else:
        raise Exception("The klasname is not found on eduflex")

# Main function
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("Run 'klas_helper add <FRIENDLY_NAME> <KLAS_NAME>' to add a klas to the JSON file")
        print("Run 'klas_helper remove <FRIENDLY_NAME>' to remove a klas from the JSON file")
        print("Run 'klas_helper list' to list all klasses inside the JSON file")
        exit(1)

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) != 4:
            print("Usage: klas_helper add <FRIENDLY_NAME> <KLAS_NAME>")
            exit(1)
        add_klas(sys.argv[2], sys.argv[3])
        
    elif command == "remove":
        if len(sys.argv) != 3:
            print("Usage: klas_helper remove <FRIENDLY_NAME>")
            exit(1)
        remove_klas(sys.argv[2])

    elif command == "list":
        list_klas()

    else:
        print("Invalid command")