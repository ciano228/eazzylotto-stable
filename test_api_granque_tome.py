import requests

# Test API granques
response = requests.get("http://localhost:8881/api/granques/mundo")
print("=== API GRANQUES ===")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test API tomes  
response = requests.get("http://localhost:8881/api/tomes/mundo")
print("\n=== API TOMES ===")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")