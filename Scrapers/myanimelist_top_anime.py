import json, requests
from bs4 import BeautifulSoup

with open("../Data/oped_alt_titles_flip_flop.json", 'r') as file:
    data_flip_flop = json.load(file)
with open('../Data/oped_anime_data.json','r') as file:
    data_all = json.load(file)
data_names = [x.lower().replace(' ','') for x in data_all.keys()]
ff_names = [x.lower().replace(' ','') for x in data_flip_flop.keys()]
#print(*ff_names,sep='\n')



page = 'https://myanimelist.net/topanime.php?type=bypopularity&limit=200'
soup = BeautifulSoup(requests.get(page).text, "html.parser")

names = soup.findAll('h3', {'class': 'hoverinfo_trigger fl-l fs14 fw-b anime_ranking_h3'})
cntr = 0
for x in names:
    xl = x.text.lower().replace(' ','')
    if xl in data_names:
        print(f"\t\"{x.text}\",")
        cntr += 1
    elif xl in ff_names:
        try:
            print(f"\t\"{data_flip_flop[x.text]}\",")
            cntr += 1
        except KeyError:
            pass
            #print(f"\t\"{x.text}\",\t\t\t<-- KEYERROR HERE")
    else:
        pass
        #print(f"\t\"{x.text}\",\t\t\t<-- IDENTIFYING ERROR HERE")

print(f"Found {cntr} out of the 50 for this page.")

