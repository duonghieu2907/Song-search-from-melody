import requests
from base64 import b64encode

client_id = "c36ea548c7764f38bd56444830b26d11"
client_secret = "280e091866db4ac6ac5456229fa85ea2"
redirect_uri = "https://www.google.com.vn/"
code = "AQA5CPi2_EF0RZDXmqzaPG9sAGG9L-aD0ROZDNZoee6uTJQfMaJjNooJduyOQE4sercpQ4hCkmh_y8nP2WuhEwtUr8EAzueBrC1qf6mP41j7Fqe2uz3hXvQRrJDWmfXGTnmVKhIRDCyeeSJW6-E-B7ohOqSjLm0gvExQeLGLN-wnEF2qj5hllAoCI065HhfuXQ"

token_url = "https://accounts.spotify.com/api/token"
# Encode the client_id and client_secret in base64 for Basic Authentication
auth_header = b64encode(f"{client_id}:{client_secret}".encode("ascii")).decode("ascii")

# Set up the headers for the request
headers = {
    "Authorization": f"Basic {auth_header}"  # Properly formatted Basic Auth header
}
data = {
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": redirect_uri
}

# Get the access token
response = requests.post(token_url, headers=headers, data=data)

# Check if the response is successful
if response.status_code == 200:
    token_data = response.json()
    access_token = token_data.get("access_token")
    if access_token:
        print("Access Token Retrieved Successfully")

        # Now use the access token to search for tracks
        search_url = "https://api.spotify.com/v1/search"
        params = {
            "q": "Vietnamese music",
            "type": "track",
            "limit": 10
        }

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(search_url, headers=headers, params=params)

        # Check if the search request was successful
        if response.status_code == 200:
            data = response.json()
            # Output track names and their artists
            for track in data['tracks']['items']:
                print(f"Track Name: {track['name']}, Artist: {track['artists'][0]['name']}")
        else:
            print(f"Error: Unable to search tracks. Status Code: {response.status_code}")
            print(f"Error Message: {response.json()}")
    else:
        print("Error: 'access_token' not found in the response.")
else:
    print(f"Error: Unable to retrieve access token. Status Code: {response.status_code}")
    print(f"Error Message: {response.json()}")

