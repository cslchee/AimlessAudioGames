import json, requests
from bs4 import BeautifulSoup

with open("Data/oped_anime_data.json", 'r') as file:
    data = json.load(file)
print(json.dumps(data, separators=(',', ':')))


page = 'http://127.0.0.1:8887/known_game_data.json'
soup = BeautifulSoup(requests.get(page).text, "html.parser")
print(soup.text)