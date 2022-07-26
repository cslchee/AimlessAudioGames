"""
JSON of all Steam Games and IDs https://raw.githubusercontent.com/dgibbs64/SteamCMD-AppID-List/master/steamcmd_appid.json

Also consider:
    recent_games_page = 'http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={API_KEY}&steamid={my_id}&format=json'
TODO Check if the user left a negative review on the game. [Very difficult]
TODO Can't identify Deltarune since it's a demo...?
TODO Some indie game's soundtracks only exist as single, long videos...

Scrapetube Documentation: https://scrapetube.readthedocs.io/en/latest/
"""
import json, random, re, requests, subprocess, urllib.parse, urllib.request
import random
from time import sleep
from bs4 import BeautifulSoup
import scrapetube

remake_terms = ('remastered', 'edition', 'enhanced', 'goty', 'definitive', 'anniversary', "director's cut",
                'game of the year', 'special')  # "Director's Cut", "Complete", "Ultimate" aren't that helpful...
playlist_start = "https://www.youtube.com/playlist?list="


def get_games_and_data(page: str) -> dict:
    soup = BeautifulSoup(requests.get(page).text, "html.parser")

    data_ids = json.loads(soup.text)['response']['games']
    # print(json.dumps(data_ids, indent=3))

    with open('../Data/known_game_data.json', 'r') as file:
        known_games = json.load(file)
    game_dict = {}
    new_games = {}
    for x in data_ids:
        the_id = str(x['appid'])
        already_known = the_id in known_games.keys()
        if already_known:  # Already did the scraping work
            if known_games[the_id] == "NA":
                continue
            name = known_games[the_id]['name']
            tags = known_games[the_id]['tags']
            devs = known_games[the_id]['devs']
            pubs = known_games[the_id]['pubs']
        else:
            url = f"https://store.steampowered.com/app/{the_id}/"
            print(f"New: {url}\t", end='')
            sleep(random.uniform(1, 2.5))  # mess with the anti-bot a bit
            soup = BeautifulSoup(requests.get(url).text, 'html.parser')

            name = str(soup.find('div', {'id': 'appHubAppName'}))
            try:
                name = name[name.index('id=') + 19:name.index('</div>')]

                #Name Processing
                name = name.encode('ascii', 'ignore')  # no \u characters
                name = name.decode()
                for grammar in (':', ';', ',', '!', '?', '/', '_'):
                    name = name.replace(grammar, ' ')
                name = name.replace('  ', ' ')  # double spaces
                name = name.strip().title()
                #Using title() exposes roman numeral names, correct Dark Souls III into Dark Souls 3
                name = name.replace('Iii','3').replace('Ii','2') #TODO Different between Metal Gear V and Metal Gear 5?
                print(name)
            except ValueError as e:
                new_games[the_id] = "NA"
                print("Error finding name on page. Probably default to Steam's front page.",
                      "This item probably isn't available on the Steam store anymore.)")
                # TODO Can still use 'SteamDB'... https://steamdb.info/app/123.../
                continue

            # Get all developers under the 'developers_list', convert to a string (via the sub-loop), and remove 'href' parts to get dev
            try:
                devs = [d[d.index('>') + 1:d.index('</a>')] for d in
                        [str(x) for x in soup.find('div', {'id': 'developers_list'}).findAll('a')]]
            except AttributeError:
                print('No Devs')  # Publishers only - rare
                devs = []

            # Working around getting publisher info from the second class='dev_row'. Make specific section into a string and split via '</a>'. Then remove 'href' part.
            pubs = [e for e in [p[p.index('>') + 1:] for p in
                                str(soup.findAll('div', {'class': 'dev_row'})[1]).split('\n')[3].split('</a>')] if
                    e]  # finally, remove potential empty

            # Find all elements with the id 'app_tag'
            tags = [t[t.index('>') + 1:t.index('</a>')].strip() for t in
                    [str(t) for t in soup.findAll('a', {'class': 'app_tag'})]]

        game_dict[name] = {
            'id': the_id,
            "devs": devs,
            "pubs": pubs,
            "playtime": int(x['playtime_forever']),
            "tags": tags
        }
        if not already_known:
            # don't keep this user's playtime
            new_games[the_id] = {
                "name": name,
                "devs": devs,
                "pubs": pubs,
                "tags": tags
            }

    if new_games:
        print(f"Adding {len(new_games)} new games to local database")
        combined_dict = {**known_games, **new_games}
        with open('../Data/known_game_data.json', "w") as file:
            file.write(json.dumps(combined_dict, indent=4))
    # print(json.dumps(game_dict, indent=4))
    return game_dict


def filter_games(game_dict: dict, playtime_minimum=0, always_musical_games=False) -> tuple:
    """
    playtime_minimum is in hours

    Ask for game specifications:
        -Played over 5-25 hours
        -Top 5-25% most played
        -Always include 'musical' games (see 'musical_tags')
    """
    if playtime_minimum < 0:
        raise ValueError("Cannot have a playtime lower than 0")
    elif playtime_minimum > 500:
        raise ValueError("Unhelpfully large minimum value (over a five-hundred hours)")

    ignore_names = ('blender', "garry'smod", 'driver4vr', 'ovrtookit', 'tabletopsimulator', 'grandtheftautov', 'vrchat',
                    'zerocalibervr', 'pavlovvr', 'segamegadriveandgenesisclassics', 'goatsonabridge', 'echogrotto',
                    'guidedmeditationvr', 'witchingtowervr', 'tulpa', 'glittermittengrove','david.','scanner sombre',
                    'planetside 2 - test','toribash')
    general_ignore_tags = ('Utilities', 'Software', 'Video Production', 'NSFW', 'Trading Card Game')
    # Audio Production gets a few mistakes

    not_a_game_words = ('Demo', 'Soundtrack', 'Dlc', 'Hentai')

    irrelevant_devs_pubs = ('Codemasters', 'Sports Interactive', 'Out of the Park Developments', 'Playground Games',
                            'BeamNG', 'Ghost Games', 'CarX Technologies, LLC', 'Visual Concepts', "Yuke's Co., LTD",
                            'HB Studios Multimedia Ltd.', 'Metalhead Software Inc.', 'Tiburon', 'Landfall')
    series_names = ('Fifa ', 'Football Manager', 'Out of the Park Baseball', 'Forza ', 'Wwe', 'Pga',
                    'Franchise Hockey Manager', 'Viscera Cleanup', "You Don'T Know Jack", "Back To The Future",
                    'Madden Nfl', 'Nba', 'Strong Bad', 'Flight Simulator', 'Final Hours','Shenzhen I O',
                    "F.E.A.R.", 'Wraith The Oblivion','Phasmophobia','Karma.','Paper Fire Rookie',
                    # 99% Licensed music:
                    'Rocksmith', 'Electronauts', 'Emily Is Away')
    musical_tags = ('Great Soundtrack', 'Rhythm', 'Music')

    filter_list = []
    ignored = {}
    reason = ""  # Troubleshooting
    game_names = tuple(game_dict.keys())
    for count, game_name in enumerate(game_names, start=1):
        acceptable = True
        compact_name = game_name.lower().replace(' ', '')
        devs_pubs = tuple(set(game_dict[game_name]['devs'] + game_dict[game_name]['pubs']))
        playtime_hrs = round(game_dict[game_name]['playtime'] / 60, 1)
        tags = game_dict[game_name]['tags']

        # BASIC TESTS
        if game_name in filter_list:
            reason = "Duplicate game"
            acceptable = False
        elif any(x for x in game_name.split() if x in not_a_game_words):  # Demos, soundtracks, etc.
            reason = "Not a game Demos, soundtracks, etc"
            acceptable = False
        elif playtime_hrs == 0:
            reason = "Playtime is 0"
            acceptable = False
        elif playtime_minimum != 0 and playtime_hrs < playtime_minimum:
            if not (always_musical_games and any(
                    x for x in musical_tags if x in tags)):  # Ignore playtime on 'great music'
                reason = f"Playtime is below given threshold of {playtime_minimum}"
                if always_musical_games:
                    reason += " and it's not 'musical'"
                acceptable = False
        elif compact_name in ignore_names:
            reason = "Manually ignored game"
            acceptable = False
        elif any(x for x in tags if x in general_ignore_tags):  # Bad tags
            reason = f"Ignored tag - Tags: {tags}"
            acceptable = False
        elif any(x for x in devs_pubs if x in irrelevant_devs_pubs):
            reason = "Irrelevant developer/publisher"
            acceptable = False
        elif any(x for x in series_names if x in game_name):
            reason = "Franchise/series name"
            acceptable = False

        # Checkpoint
        if not acceptable:
            ignored[game_name] = reason
            continue

        # Complex filter
        if any(remake_term in compact_name for remake_term in remake_terms):
            no_term = game_name.lower()
            for r in remake_terms:
                no_term = no_term.replace(r.lower(), '')
            no_term = no_term.replace('-', '').replace('  ', ' ').strip()

            cont_flag = False
            for key in game_names:
                if key == game_name:
                    continue
                elif key.lower() == no_term:  # Shallow exact-text comparison
                    # print(f"\t\t\t{no_term}  and  {key.lower()}")
                    ignored[game_name] = "Already has another remastered/GOTY/Enhanced edition of this game"
                    cont_flag = True
                    break
            if cont_flag:
                continue
        # TODO Situational with DS Remastered and DS Prepare to Die Edition...

        # Episode-Remover
        if "Sam &Amp Max" in game_name and "Telltale Games" in devs_pubs:
            if "10" in game_name:
                game_name = "Sam and Max Save The World"
            elif "20" in game_name:
                game_name = "Sam and Max Beyond Space and Time"
            elif "30" in game_name:
                game_name = "Sam and Max Devil's Playhouse"
        elif "Episode" in game_name:
            game_name = game_name[:game_name.index("Episode")].replace(" - ", '').strip()
        if game_name in filter_list:
            reason = "Episode/Telltale duplicate"
            acceptable = True

        # FINAL CHECK
        if not acceptable:
            ignored[game_name] = reason
            continue
        filter_list.append(game_name)
        # print(f"\t{game_name:25}  -  {playtime_hrs}")
    print(f"Ignored games:")
    for k, v in ignored.items(): print(f'\t{k}: {v}')

    return tuple(sorted(set(filter_list)))


def get_OST_playlist(search_term, game) -> tuple:
    playlist_id = p_title = ""
    irrelevant_playlist = ('extended', 'extension', 'cover', "let's play", 'lets play', 'walkthrough', 'playthrough',
                           'favorite', 'study', 'full game', '100%')
    playlists = scrapetube.get_search(search_term,
                                      limit=8, #Occasionally takes time to find exact phrasing
                                      sort_by="view_count",
                                      results_type="playlist")
    for p in playlists:
        p_title = p['title']['simpleText']
        print(f"\t\t{p_title:25} --> {p['videoCount']} vids   ({playlist_start}{p['playlistId']})", end='  ')
        if any(x for x in irrelevant_playlist if x in p_title.lower().split()):  # Avoid extended-plays
            continue

        if int(p['videoCount']) > 250:  # Avoid massive compilations
            print('X - Massive!')
            continue
        if len(p_title) < len(game) or len(p_title) > 100:  # playlists called 'OST' or with massive titles
            print('X - Title is too short/long')
            continue
        #Catch playlists for incorrect sequels - Ex: Looking for 'bayonetta ost', got 'bayonetta 2 ost'
        seq_flag = False
        for sequel in ('2','3'):
            space_seq = f' {sequel}'
            if game.endswith(space_seq) and space_seq not in p_title:
                print(f'X - Not a playlist for the sequel ({sequel})')
                seq_flag = True
                break
            elif not game.endswith(space_seq) and space_seq in p_title:
                print(f'X - Not a playlist for the this version ({sequel})')
                seq_flag = True
                break
        if seq_flag:
            continue

        p_set = set(p_title.replace(' - ', ' ').replace(':', '').replace("'", '').lower().split())
        g_set = set(game.lower().split())

        # Contains the name and the playlist are listed as soundtrack
        if all(x in p_set for x in g_set) and any(x for x in ('ost', 'soundtrack') if x in p_title.lower()):
            playlist_id = p['playlistId']
            print("✓")
            break
        else:
            print("X")

    return playlist_id, p_title


def get_OSTs(games: tuple, manually_provide_playlist=False, elaborate_search=False) -> dict:
    music_entries = {}
    with open('../Data/known_game_music.json', 'r') as file:
        known_music = json.load(file)

    for g in games:
        for x in remake_terms:
            g = g.replace(x, '')
        for x, y in (('&Amp', '&'), (':', ''), (' - ', ' '), ('  ', ' ')):  # ('+', ' plus ')
            g = g.replace(x, y)
        g = g.strip()
        if g in tuple(known_music.keys()):
            music_entries[g] = known_music[g]
        else:
            # Find a valid OST playlist
            search_term = f"{g.lower()} ost"  # 'soundtrack' vs 'OST'?   {' video game' if len(g) < 10 else ''}
            print(f'~Finding OST for "{search_term}":')

            # TODO If bad results, do search again using different 'sort_by' or by adding in 'game' before 'ost'

            playlist_id, p_title = get_OST_playlist(search_term,game=g)

            if elaborate_search and not playlist_id:
                playlist_id, p_title = get_OST_playlist(f"{g.lower()} game ost", game=g)
                #could do a for-loop of even more tries... ('relevance', 'view_count', 'rating')

            if playlist_id == "" and not manually_provide_playlist:
                print(f"\tX___Could not find a playlist for {g}")
                continue
            elif manually_provide_playlist:
                manual_playlist = ""
                if not playlist_id:
                    print(f"\tCould not find a playlist for {g}")
                else:
                    print(
                        f"\tGoing to use {playlist_start}{playlist_id}. Is this okay? (Any = Yes | Enter = Manually Enter)")
                    manual_playlist = input("\t>_")
                if not manual_playlist:
                    next_game_instead = False
                    # Input Verification
                    while True:
                        print("\tPlease manually enter the playlist's ID or URL")
                        print(
                            f"\t\thttps://www.youtube.com/results?search_query={'+'.join(search_term.split())}&sp=EgIQAw%253D%253D")
                        print("\t\t(Enter to Skip)")
                        manual_playlist = input("\t\t>_")
                        if manual_playlist == "":
                            next_game_instead = True
                            break
                        if len(manual_playlist) != 41 and playlist_start not in manual_playlist: #Not quite right...
                            print("\tIt has to be 41 characters if it's just an ID. Try again")
                            continue
                        elif len(manual_playlist) > 79 and playlist_start in manual_playlist:   #Not quite right...
                            print("\tIt has to be les than 79 characters if it's a full URL (I think?). Try again")
                            continue
                        playlist_id = manual_playlist.replace(playlist_start, '')
                        break
                    if next_game_instead:
                        continue

            music_entry = {
                'playlist_title': p_title,
                'playlist_id': playlist_id,
                'videos': []
            }

            # Get all the video ids and titles
            print(f"\tGetting videos from {playlist_start}{playlist_id}")
            videos = scrapetube.get_playlist(playlist_id)
            videos_are_okay = True
            for count, v in enumerate(videos):
                length = int(v['lengthSeconds'])
                if length < 15: continue  # ignore jingles
                v_title = v['title']['runs'][0]['text']
                if count < 5:
                    print('\t', v_title)
                elif count == 5:
                    print('\t ....')
                if 'lets play' in v_title.lower().replace("'", ''):
                    videos_are_okay = False
                    print(f"\t>>Bad video: {v_title}\n\tSkipping!")
                    break

                music_entry['videos'].append({
                    "title": v_title,
                    "id": v['videoId'],
                    "length": length
                })

            if videos_are_okay:
                music_entries[g] = music_entry
                # update it every time if it's being done manually
                if manually_provide_playlist:
                    with open('../Data/known_game_music.json', 'w') as file:
                        file.write(json.dumps({**known_music, **music_entries}, indent=4))

    input("HALT! Review the above! >_")
    with open('../Data/known_game_music.json', "w") as file:
        file.write(json.dumps({**known_music, **music_entries}, indent=4))

    return music_entries


def play_yt_video_audio(music) -> None:
    pass


def main():
    all_ids = {
        "me": 76561198032632811,
        "michael": 76561198145257760,
        "liz": 76561198207764489,
        "curtis": 76561198068361043,
        "nick": 76561198307602151,
        "bennett": 76561198143431157,
        "eli": 76561198076322721,
        "ethan": 76561198068272400,
        "brengis": 76561198241791244,
        "eric": 76561197996479889,
        #"ian_chapman": 76561198045704747, #privated games
        "myth": 76561197960777546
    }
    # https://www.steamidfinder.com/

    for name, my_id in all_ids.items():
        print(f"{'- '*20}\nChecking out {name}\n{'- '*20}")
        API_KEY = "4130330FD6DE87CA2759338B96909684"
        games_page = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={my_id}&format=json"

        game_dict = get_games_and_data(games_page)
        games_selected = filter_games(game_dict)  # Recommend >1

        music = get_OSTs(games_selected, manually_provide_playlist=False, elaborate_search=False)

    exit() #TODO TESTING BREAK HERE - - - - - - - - - - - -

    # print(f"Filter Games:")
    # for g in games_selected: print(f"\t{g}")
    # print(f"Length of games_selected: {len(games_selected)}")



    # TODO Should get image using "https://i.ytimg.com/vi/__ID__/maxresdefault.jpg"


if __name__ == '__main__':
    main()
