import json, requests
from bs4 import BeautifulSoup

with open("../Data/oped_alt_titles_flip_flop.json", 'r') as file:
    data_flip_flop = json.load(file)
with open('../Data/oped_anime_data.json','r') as file:
    data_all = json.load(file)
ff_names = [x.lower() for x in data_flip_flop.keys()]
ff_names += [x.lower().replace(' ','') for x in data_all.keys()]
#print(*ff_names,sep='\n')



page = 'https://myanimelist.net/topanime.php'
soup = BeautifulSoup(requests.get(page).text, "html.parser")

names = soup.findAll('h3', {'class': 'hoverinfo_trigger fl-l fs14 fw-b anime_ranking_h3'})
cntr = 0
for x in names:
    if x.text.lower().replace(' ','') in ff_names:
        print(x.text)
        cntr += 1
print(f"Found {cntr}")

