import requests

def make_api_call(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print("Pogreška pri preuzimanju dokumenta:", response.status_code)
        return None
