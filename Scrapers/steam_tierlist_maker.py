import json, requests, steam_music
from bs4 import BeautifulSoup
from tkinter import filedialog


def inputVerify(message: str, low: int, high: int, neutralInput=False) -> int:
    if low > high:
        input(f"ERROR inputVerify() has received a swapped low/high: min-{low} max-{high}.\nPress any to quit.")
        exit()  # returning -1 would crash the system anyway
    while True:
        value = input(message + ">_")
        if neutralInput and value == "":  # for 'enter->select all' scenarios
            return value
        try:
            value = int(value)
        except ValueError:
            print("Not an integer value. Try again...")
            continue
        else:
            if value > high or value < low or value < 0:
                print(f"\\ \\ \\ Not with valid range[{low}->{high}]. Try again...")
            else:
                break
    return value

def filter_games(game_dict: dict) -> dict:
    print("Time do to some filtering")
    game_names_and_ids = {}
    hours_minimum = 0
    
    if inputVerify("\t1-Choose Parameters\n\t2-Fuck it, do everything",1,2) == 1:
        # Customize Hours  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
        max_hrs = 0
        for x in game_dict.keys():
            if game_dict[x]['playtime'] > max_hrs:
                max_hrs = game_dict[x]['playtime']
        max_hrs = round(max_hrs, 1)

        avg_hrs = 0
        for x in game_dict.keys():
            avg_hrs += game_dict[x]['playtime']
        avg_hrs = round(avg_hrs / len(game_dict) / 60, 1)

        print(f"Playtime Filter:\n\t(Unplayed already removed)", end='\n\t')
        hrs_mode_tuple = ("All Played (sub-hour)",
                          "Any Above 1 Hour",
                          f"Above Average Playtime ({avg_hrs} hrs)",
                          "Top X Most Played",
                          "Custom")
        for index, x in enumerate(hrs_mode_tuple, start=1):
            print(f"{index}-{x}", end='\n\t')
        hrs_type = inputVerify("", 1, len(hrs_mode_tuple))
        if hrs_type == 1:
            hours_minimum = 0
        elif hrs_type == 2:
            hours_minimum = 1
        elif hrs_type == 3:
            hours_minimum = avg_hrs
        elif hrs_type == 4:
            hrs_places = inputVerify("How many many of your most played games? (Top 5 - 50) ", 5, 50)
            hours_list = []
            for x in game_dict.keys():
                if game_dict[x]['playtime'] > 0:
                    hours_list.append(game_dict[x]['playtime'])
            hours_list.sort(reverse=True)
            print(hours_list)
            hours_minimum = round(hours_list[hrs_places-1] / 60, 1)
            print(hours_minimum)
        elif hrs_type == 5:
            hours_minimum = inputVerify("What is the minimum time hours-played you'd like to include?", 1, max_hrs)


    #Add filtered games into the list
    for game in tuple(game_dict.keys()):
        tags = game_dict[game]['tags']
        if game_dict[game]['playtime'] == 0: #no playtime
            continue
        elif 'dlc' in game.lower():
            continue
        elif any(x for x in tags if x in ('Utilities', 'Software', 'Video Production')): #general_ignore_tags
            continue

        #final check and append
        if round(game_dict[game]['playtime']/60, 1) >= hours_minimum:
            game_names_and_ids[game] = game_dict[game]['id']
    
    return game_names_and_ids

def download_get_client_icons(game_names_and_ids: dict) -> None:
    for game, id in game_names_and_ids.items():
        soup = BeautifulSoup(requests.get(f"https://steamdb.info/app/{id}/info/").text, 'html.parser')

        icons = soup.findAll('a')
        # TODO FUCKING CLOUDFLARE
        # - - - - - - -
        icons = soup.find('div', {'id': 'info'}).findAll('a')[0]
        print(str(icons))


def label_client_icons(game_list: tuple) -> None:
    pass

def main():
    API_KEY = "4130330FD6DE87CA2759338B96909684"
    games_page = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={76561198032632811}&format=json"

    game_dict = steam_music.get_games_and_data(games_page)
    game_names_and_ids = filter_games(game_dict)
    print(json.dumps(game_names_and_ids))
    download_get_client_icons(game_names_and_ids)

    # print(f"Going to download {___} images.\nChoose a download location!")
    # sleep(1)
    # folder_selected = filedialog.askdirectory()
    # print(folder_selected)




if __name__ == '__main__':
    main()
