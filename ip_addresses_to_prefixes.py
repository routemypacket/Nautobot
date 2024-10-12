import requests
import ipaddress
import json

# Nautobot API details
NAUTOBOT_API_URL = "http://your-nautobot-instance/api/ipam/prefixes/"
NAUTOBOT_API_TOKEN = "your-nautobot-api-token"

# Headers for API authentication
headers = {
    "Authorization": f"Token {NAUTOBOT_API_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Step 1: Fetch IP addresses from Nautobot
def get_ip_addresses():
    url = "http://your-nautobot-instance/api/ipam/ip-addresses/"
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises error for bad responses
    ip_addresses = response.json()["results"]
    return [ip["address"] for ip in ip_addresses]

# Step 2: Calculate prefixes from the IP addresses
def calculate_prefixes(ip_addresses):
    prefixes = set()
    for ip in ip_addresses:
        network = ipaddress.ip_network(ip, strict=False)  # Allow creation of a network from any IP
        prefixes.add(network.with_prefixlen)
    return prefixes

# Step 3: Check if a prefix exists in Nautobot
def prefix_exists(prefix):
    url = f"{NAUTOBOT_API_URL}?prefix={prefix}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["count"] > 0  # If count > 0, prefix exists

# Step 4: Create a new prefix in Nautobot
def create_prefix(prefix):
    data = {
        "prefix": prefix,
        "status": "active",  # Set the status of the prefix
        "description": "Auto-created from existing IP addresses",
    }
    response = requests.post(NAUTOBOT_API_URL, headers=headers, data=json.dumps(data))
    response.raise_for_status()  # Raise error if the request fails
    return response.json()

def main():
    try:
        # Fetch IP addresses from Nautobot
        ip_addresses = get_ip_addresses()
        
        # Calculate unique prefixes
        prefixes = calculate_prefixes(ip_addresses)
        
        # Step 5: Create the first prefix that doesn't already exist
        for prefix in prefixes:
            if not prefix_exists(prefix):
                # Create the prefix in Nautobot
                result = create_prefix(prefix)
                print(f"Successfully created prefix: {result['prefix']}")
                return  # Stop after creating the first prefix
        print("No new prefixes were created (all prefixes already exist).")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

if __name__ == "__main__":
    main()
