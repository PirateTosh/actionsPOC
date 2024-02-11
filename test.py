import requests

url = (
    "http://localhost:5000/omegaTron_test"  # Replace <port> with the actual port number
)
response = requests.get(url)

if response.status_code == 200:
    print("API endpoint reached successfully.")
    print("Response:", response.text)
else:
    print("Failed to reach API endpoint. Status code:", response.status_code)
