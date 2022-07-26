import json

with open('../Data/oped_anime_data.json', 'r') as file:
    data = json.load(file)

all_genres = set()

for key in tuple(data.keys()):
    genres = data[key]['genres']
    if genres:
        for g in genres:
            all_genres.add(g)

all_genres = sorted(all_genres)
print(all_genres)
