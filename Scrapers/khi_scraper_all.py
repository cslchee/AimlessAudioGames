import json, requests
from random import uniform
from time import sleep
from bs4 import BeautifulSoup

with open('../Data/khi_data.json', 'r') as file:
    data = json.load(file)
khinsider_url = "https://downloads.khinsider.com/"
base_browse_url = f'{khinsider_url}game-soundtracks/browse/'
obscure_retro_systems = ('3DO','Amiga','Atari 8-Bit','Atari Jaguar','Atari ST','CD-i','Commodore 64','FDS','FM Towns',
                         'Fujitsu FM77AV','IBM PC','IBM PC/AT','PC-88','PC-98','PC-9821','PC-FX','Sharp X1','Spectrum',
                         'TurboGrafx-16','X68000','FM Towns','Anime','Movie')
                        #Also include, 'Family Computer', 'MS-DOS'?
unwanted_album_types = ('Remix','Arrangement','Inspired By','Compilation') #Skipping empty would mean skipping some good underdocumented albums

def wait_a_sec():
    sleep(uniform(5.5, 10.5)) # Easy off DDOS/Banning potential

def convert_to_seconds(timecode: str) -> int:
    """Converts timecodes (ex 1:30) into raw seconds (ex 90)"""
    split_code = timecode.split(':')
    return int(split_code[0]) * 60 + int(split_code[1])

def recheck_details_for_album_type_and_platform(soup: BeautifulSoup) -> bool:
    platforms = []
    album_type = ''
    summary = soup.find('p', {'align': 'left'}).text.split('\n')
    for text in summary:
        if 'Platforms: ' in text.strip():
            platforms = [x.strip() for x in text.replace('Platforms:', '').strip().split(',')]
        if "Album type: " in text.strip():  # lower-case 't'
            album_type = text.replace('Album type:', '').strip()
    # Skip if it's ONLY ON obscure platforms or a bad album type
    return album_type in unwanted_album_types or all(x in obscure_retro_systems for x in platforms)  # if Platforms is full subset


def page_album_data(album_url: str):
    global data
    data_temp = {
        "album_url": album_url.replace(f'{khinsider_url}game-soundtracks/album/',''), #Used for checking for duplicates while scraping
        "platforms": [],
        "year": "",
        "developer": [],
        "publisher": [],
        "thumbnail": "",
        "songs": {}
    }
    soup = BeautifulSoup(requests.get(album_url).text, "html.parser")

    # Do a second filter for undesired album types and platforms bc requests from a 'category-based' query don't get that initial change to do so
    if recheck_details_for_album_type_and_platform(soup):
        print(' - Skipped due to platform or album type -  ', end='')
        return

    title = soup.find('div', {'id': 'pageContent'}).find('h2').text


    # Get the first album cover
    try:
        temp = soup.find('div', {'id': 'pageContent'}).find('table').find('img')['src']
        # Remove the predictable from of the url, host might change
        data_temp['thumbnail'] = temp[temp.index('/soundtracks/')+13:].replace(f'{data_temp["album_url"]}/thumbs/','')
    except:
        data_temp['thumbnail'] = ""

    # Format and dissect page content
    page_content = soup.find('div', {'id': 'pageContent'}).findAll('p') # Could also visit 'khinsider.info.txt' url extension for raw 'p' info
    # First 'p' is sometimes alternative album titles, the 'p' with content doesn't have a class
    page_content_index = 1 if page_content[0].has_attr('class') else 0
    page_content = page_content[page_content_index].text
    page_content = [x.strip() for x in page_content.split('\n') if len(x.strip()) != 0]
    #print(page_content)
    platforms = []
    for line in page_content:
        if 'Platforms:' in line:
            platforms = line.replace('Platforms: ','').split(', ')
            data_temp['platforms'] = platforms
        elif 'Year:' in line:
            data_temp['year'] = line.replace('Year: ','')
        elif 'Developed by: ' in line:
            data_temp['developer'] = line.replace('Developed by: ', '').split(', ')
        elif 'Published by: ' in line:
            data_temp['publisher'] = line.replace('Published by: ','').split(', ')

    # Validate useful album (not 'Anime'/'Movie' or an obscure retro console)
    if all(x in platforms for x in obscure_retro_systems): # Test for full subset
        return

    songs = {}
    for song in soup.find('table', {'id': 'songlist'}).findAll('tr')[1:-1]: #skip 'tr' header and 'total' row
        #Find the length of the song, document it, discard it if it's too short
        song_info = song.text.split('\n')
        for song_text_detail in song_info:
            if ':' in song_text_detail:
                timecode_split = song_text_detail.split(':')
                # Verify that the split string with a ':' in it isn't like 'Chapter 1: The End' instead of '1:23'
                if len(timecode_split) == 2 and timecode_split[0].isnumeric() and timecode_split[1].isnumeric():
                    song_length = convert_to_seconds(song_text_detail)
                    break
        try:
            if song_length < 30: # I need this to cause an error if song_length can't be found bc there might be more errors like it
                continue
        except UnboundLocalError:
            print('Song length not found. Skipping.  ' ,end='')
            continue
            #raise Exception(f"The found length of the song was either not found or isn't numeric: {song_length}\n{song_info}")

        info_box = song.find('a') #just the first one
        song_name = info_box.text.replace('.mp3','')
        song_source_page = BeautifulSoup(requests.get(f"https://downloads.khinsider.com{info_box['href']}").text, "html.parser")
        song_source = song_source_page.find('audio')['src']
        song_source = song_source[song_source.index('/soundtracks/')+13:] #Might have different hosting sites...
        song_source = song_source.replace('.mp3','') #Assuming none of the first links will be .FLACs
        song_source = song_source.replace(f"{data_temp['album_url']}/",'') #URLs always start with the album URL too
        #We are no longer recording the song length since we can get it during javascript
        songs[song_name] = song_source
    #print(json.dumps(songs, indent=2))

    #If the whole album was just bits of sounds, don't grab it (every instance of song_length ended up in a 'continue')
    if len(songs) < 5:
        print("This soundtrack is too short and/or has short songs in it. Skipping.  ", end='') #Avoids some random music singles
        return

    data_temp['songs'] = songs

    data |= {title: data_temp}

def get_all_page_albums_detailed_columns(page_url: str, page: int) -> list:
    """Acquire the links to all the albums on a single page, filtering out remixes/arrangement/compilation type albums"""
    if 'search?' not in page_url: # Searches on khinsider display 1000 results at once, there are no pages
        page_url += f"?page={page}"
    soup = BeautifulSoup(requests.get(page_url).text, "html.parser")
    # No filtering, one line
    #albums = [x.findAll('a')[1]['href'].replace('/game-soundtracks/album/','') for x in soup.find('div', {'class': 'albumListDiv'}).findAll('tr') if len(x.findAll('td')) != 0] #first 'tr' is the headers

    # Filter out any 'Remix' or 'Arrangement' albums (could be fan-made stuff)
    albums = []
    skipped_count = 0
    for album in soup.find('div', {'class': 'albumListDiv'}).findAll('tr')[1:]: #Skip the header row
        link_to_album = album.findAll('a')[1]['href'].replace('/game-soundtracks/album/', '')
        # Get <td> info as text, find the album type
        album_type = [x.strip() for x in album.text.split("\n")][7]
        platforms =  [y.strip() for y in [x.strip() for x in album.text.split("\n")][6].split(',')]
        # Only grap basically 'Gamerip' and 'Soundtrack'. (Allow 'empty', some of the good ones are under-documented)
        if album_type in unwanted_album_types or all(x in obscure_retro_systems for x in platforms):
            skipped_count += 1
            continue
        albums.append(link_to_album)
    print(f"\n{'- '*20}\n{page_url}\n{'- '*20}\nPage {page} - {len(albums)} albums to scrape - Skipped {skipped_count} Remix/Arrangement/Etc albums\n{albums}")
    return albums

def get_all_page_albums_categories(category_url, page: int) -> list:
    """Based on 'letters' variety, but the HTML is different. No platform, year, rip columns either."""
    soup = BeautifulSoup(requests.get(f"{category_url}?page={page}").text, "html.parser")

    albums = []
    for album in soup.find('table').findAll('tr')[1:]:
        albums.append(album.findAll('a')[1]['href'].replace('/game-soundtracks/album/', ''))

    return albums

def get_all_album_urls(albums_pages: list) -> list:
    all_albums_urls = []
    for page in albums_pages:
        soup = BeautifulSoup(requests.get(page).text, "html.parser")

        #Find the page count
        if 'top40' in page:
            page_count = 1
        elif 'top-100' in page: #remember, 100 means 1000
            page_count = 10
        else:  # Get number of pages for letter-based searches
            try:
                page_count = int(soup.find('div', {'class': 'pagination'}).find('a', {'title': 'End'})['href'][-1])
                if page_count <= 0:
                    raise Exception(f"Looks like there's something wrong with the initial page_count (it's currently {page_count})")
            except AttributeError: #nonetype for find()
                page_count = 1

        #cycle through the rest of pages - filter into either general letter scraper or the differently-formatted top lists
        for p in range(page_count):
            if any([x for x in ['top','most-favorites'] if x in page]):
                all_albums_urls += get_all_page_albums_categories(page, page=p+1)
            else:
                all_albums_urls += get_all_page_albums_detailed_columns(page, page=p + 1)

        wait_a_sec()
    return all_albums_urls

def scrape_khi_albums(all_albums_urls: list) -> None:
    """Visit each album page and scrape the media info and audio tracks from it"""
    all_existing_albums_url = [data[key]['album_url'] for key in data.keys()]

    for index, album in enumerate(all_albums_urls, start=1):
        print(f"{index}. {album}  ", end='')
        if album not in all_existing_albums_url: # Check the data['album_url']s, not the titles
            album_url = base_browse_url.replace('browse', 'album') + album
            page_album_data(album_url)
            print("Done!")

            # Write all data to a JSON file. Doing it each time to avoid having to go back and redo entries
            with open('../Data/khi_data.json', 'w') as final_file:
                final_file.write(json.dumps(data, indent=1))

            wait_a_sec()
        else:
            print("[Already Exists]")



#  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --

def scrape_khi_letters():
    """Get full pages sets and the delegating sub-scraping to other functions"""
    literally_all_pages = [base_browse_url + letter for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
    literally_all_pages.append(base_browse_url + '0-9') # This url represents that games that start with non-alphabetic characters
    all_albums_urls = get_all_album_urls(literally_all_pages) #This will take a very long time, take it one/two at time plz
    scrape_khi_albums(all_albums_urls)


def collect_category(category_str: str, scrape_or_category_titles: str) -> None:
    """
    Creates a category of album urls for sorting later. Not designed to be used with any 'browse'/alphabetic areas.
    Using 'titles' on 'search'-based urls isn't recommended since you could just use the title plus dev/publisher in the real game
    Examples:
        top40
        all-time-top-100 (It's actually top 1000)
        most-favorites
        search?search=pokemon (or mario, kirby, zelda, etc.)
        game-soundtracks/developer/____
        game-soundtracks/publisher/____
    """
    if scrape_or_category_titles not in ('scrape', 'titles','top1000special'):
        raise Exception("Unusable argument given to 'scrape_or_category_titles'. Please use 'scrape' or 'titles' as inputs.")

    #Acquire album urls, remove the front part to match what's in 'khi_data'
    category_url = f'{khinsider_url}{category_str}'
    all_category_album_urls = get_all_album_urls([category_url])

    if scrape_or_category_titles == "scrape":
        print(f"Now scraping for data from {f'{category_url}'}\n{'- '*25}\n")
        scrape_khi_albums(all_category_album_urls)
    elif scrape_or_category_titles == "titles": # Just for use in categories json that'll be used for sorting during gameplay
        print(f"Now scraping for filtered titles from {f'{category_url}'}\n{'- ' * 25}\n")
        # ~~ Takes more time, but checks to make sure that the title being grabbed fits good platform/album type needs
        # ~~ Note: I attempted to make a quick, unfiltered version that grabs just the title from the main page of
        #          the ten pages of the 'all-time-top-100' list, but the list is formatted differently.
        #          Instead of unique columns for each attribute, the details gets tagged onto the end of the title
        #          as raw text, i.e.:
        #             "Super Smash Bros. Anthology Vol. 01 - Super Smash Bros. (3DS, GC, N64, Switch, Wii, Wii U) (gamerip) (1999)"
        #          So, it's super tricky to dissect the real title if there's organically a parenthesis in the title, .i.e:
        #             "Minecraft Soundtrack - Volume Alpha and Beta (Complete Edition) (2011, 2013, 2019)"
        #           Which basically means that you MUST get the title via the album's info text <p>.
        #           Thank you for coming to my TedTalk
        # NOTE: While getting the album urls first (instead of simply the titles then and there) feels like a waste,
        #       it's still good to have two layers of filtering on, even if it drastically increases scrape time.

        # From the URLs, get the individual titles in order to match the keys of 'khi_data'. Taken from 'page_album_data'.
        all_category_album_titles = []
        for album_url in all_category_album_urls:
            soup = BeautifulSoup(requests.get(f'{khinsider_url}game-soundtracks/album/{album_url}').text, "html.parser")

            #There are no initial descriptors for the 'top' lists, so you'll have to check for Bad Platforms and Gamerip/Soundtrack here
            title = soup.find('div', {'id': 'pageContent'}).find('h2').text

            # As with the initial scrape of letters, skip any obscure platforms or bad album types
            if recheck_details_for_album_type_and_platform(soup):
                print(f"Skipping '{title}'") #
                continue

            all_category_album_titles.append(title)
            print(f"Added '{title}'")
            wait_a_sec()

        #Update the dictionary of categories with the new one
        with open('../Data/khi_categories.json', 'r') as file_categories:
            data_categories = json.load(file_categories)
            data_categories[category_str] = all_category_album_titles
        with open('../Data/khi_categories.json', 'w') as file_categories:
            file_categories.write(json.dumps(data_categories, indent=1))

    print("\nAll Done!")

def clean_khi_data():
    """Spot suspicious/unwanted entries from khi_data"""
    title_defects = (
        'hack','preview','bootleg','homebrew','e3 demo','prototype','promotional','unreleased',
        'pre-alpha','pre-beta','(mod)','kiosk','karaoke'
        # 'beta', 'alpha', 'demo' #Could be the name of games...
    )
    multi_part_title_defects = (
        'fan game', 'fan remake', 'fan remaster', 'friday night funkin', 'rom hack' ,'hack rom', 'bonus dvd',
        'live concert'
    )
    with open('../Data/khi_data.json','r') as file_to_clean:
        data_to_clean = json.load(file_to_clean)

    for title in list(data_to_clean.keys()):
        temp_title = title.lower().replace('(','').replace(')','')
        title_parts = [x.lower() for x in temp_title.split(' ')]
        if any(x for x in title_parts if x in title_defects):
            print(f"Removing: {title}")
            del data_to_clean[title]
            continue

        if any(x for x in multi_part_title_defects if x in title.lower()):
            print(f"Removing: {title}")
            del data_to_clean[title]

    # Uncomment to make a permanent change
    with open('../Data/khi_data.json', 'w') as file_to_clean:
        file_to_clean.write(json.dumps(data_to_clean, indent=1))


def main():
    #  Grab everything, from A->Z (with numbers too)
    #scrape_khi_letters()

    # Grab specific searches/top40/all-time-top-100 (actually 1000)
    # ~~ OR ~~
    # Set up the Categories w/ scrape_or_category_titles='titles' arg
    #collect_category('top40', scrape_or_category_titles='titles')
    #collect_category('all-time-top-100', scrape_or_category_titles='titles') #Actually the top 1000


    franchises = ('pokemon', 'mario', 'zelda', 'kirby', 'halo', 'mega+man', 'final+fantasy', 'sonc', 'street+fighter', 'metroid',
        'metal+gear+solid','kingdom+hearts', 'fire+emblem', 'animal+crossing', 'castlevania',' donkey+kong', 'kid+icarus', 'star+fox',
        'parappa+the+rapper', 'god+of+war', 'horizon', 'ori+and+the', 'crash+bandicoot', 'ratchet+and+clank', 'splatoon',
        'bioshock','hades','transistor','bastion', 'team+fortress+2','half+life','chrono+trigger','elden+ring','disco+elysium',
        'hi-fi+rush','bayonetta','ikenfell','katana+zero','fez','hyper+light+drifter','like+a+dragon',
        'monster+hunter','outer+wilds','portal','prey','psychonauts','rivals+of+aether', 'rayman','sayonara+wild+hearts',
        'shovel+knight','borderlands','spore','terraria','thumper','tunic','beat+saber+original','dragon+age','oxenfree',
        'night+in+the+woods','mirror%27s+edge','celeste','cuphead','gris', 'spiritfarer','slay+the+spire',

        'assassin%27s+creed','a+hat+in_time','metro','2064','sea+of+stars','machinarium','battleblock',
        'dishonored','resident+evil','dead+cells','sekiro','dark+souls','hylics','capcom','30xx','devil+may+cry','killer+instinct',
        'stray','ultrakill','katamari','cave+story','ftl','donut+county','jackbox','sam+and+max','monument+valley','samorost',
        'botanicula','spy+fox','pajama+sam','meat+boy','guilty+gear','frog+detective','accounting','mass+effect','witcher',
        'cyberpunk+2077','stardew+valley','going+under','inscryption','super+smash+bros','banjo-kazooie','in+stars+and+time'
        )

    # for franchise in franchises:
    #     collect_category(f"search?search={franchise.replace(' ','+')}", scrape_or_category_titles='scrape')

    #collect_category("game-soundtracks/publisher/annapurna-interactive", scrape_or_category_titles="scrape")

    clean_khi_data()



if __name__ == "__main__":
    main()
