import json, requests
from random import uniform
from time import sleep
from bs4 import BeautifulSoup

with open('../Data/khi_data.json', 'r') as file:
    data = json.load(file)
base_browse_url = 'https://downloads.khinsider.com/game-soundtracks/browse/'
obscure_retro_systems = ('3DO','Amiga','Atari 8-Bit','Atari Jaguar','Atari ST','CD-i','Commodore 64','FDS','FM Towns',
                         'Fujitsu FM77AV','IBM PC','IBM PC/AT','PC-88','PC-98','PC-9821','PC-FX','Sharp X1','Spectrum',
                         'TurboGrafx-16','X68000')
                        #Also include, 'Family Computer', 'MS-DOS'?

def wait_a_sec():
    sleep(uniform(1.5, 3.5)) # Easy off DDOS/Banning potential

def page_album_data(album_url: str):
    global data
    data_temp = {
        "platforms": [],
        "year": "",
        "developer": [],
        "publisher": [],
        "thumbnail": "",
        "songs": {}
    }
    soup = BeautifulSoup(requests.get(album_url).text, "html.parser")

    title = soup.find('div', {'id': 'pageContent'}).find('h2').text

    # Get the first album cover
    try:
        data_temp['thumbnail'] = soup.find('div', {'id': 'pageContent'}).find('table').find('img')['src'].replace(
            'https://vgmsite.com/soundtracks/', '')
    except:
        data_temp['thumbnail'] = ""

    # Format and dissect page content
    page_content = soup.find('div', {'id': 'pageContent'}).findAll('p')
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
    if len(platforms) == 1 and (platforms[0] == 'Anime' or platforms[0] == 'Movie'): # Not video games
        return
    if platforms == ['Anime','Movie']:
        return
    if all(x in platforms for x in obscure_retro_systems): # Test for full subset
        return
    # Check this before visiting each song


    songs = {}
    for song in soup.find('table', {'id': 'songlist'}).findAll('tr')[1:-1]: #skip 'tr' header and 'total' row
        info_box = song.find('a') #just the first one
        song_name = info_box.text
        song_source_page = BeautifulSoup(requests.get(f"https://downloads.khinsider.com{info_box['href']}").text, "html.parser")
        song_source = song_source_page.find('audio')['src'].replace('https://vgmsite.com/soundtracks/','')
        songs[song_name] = song_source
    #print(json.dumps(songs, indent=2))

    data_temp['songs'] = songs

    data |= {title: data_temp}


def get_all_page_albums(browse_letter, page='') -> list:
    soup = BeautifulSoup(requests.get(f"{base_browse_url}{browse_letter}?page={page}").text, "html.parser")
    albums = [x.findAll('a')[1]['href'].replace('/game-soundtracks/album/','') for x in soup.find('div', {'class': 'albumListDiv'}).findAll('tr') if len(x.findAll('td')) != 0] #first 'tr' is the headers
    print(f"{browse_letter}{page}. {len(albums)} albums - {albums}")
    return albums


def scrape_all_khi():
    #Cycle through '#', A, B, ... Z and get every album
    symbol_tuple = ['B'] #list('#ABCDEFGHIJKLMNOPQRSTUVWXYZ') #This will take a very long time
    all_albums_urls = []
    for browse_letter in symbol_tuple:
        soup = BeautifulSoup(requests.get(base_browse_url + browse_letter).text, "html.parser")

        #get number of pages
        try:
            pages = int(soup.find('div', {'class': 'pagination'}).find('a', {'title': 'End'})['href'][-1])
        except AttributeError: #nonetype for find()
            pages = 1

        #cycle through the rest of pages
        all_albums_urls += get_all_page_albums(browse_letter) #'main page' visit is redundant...
        if pages > 1:
            for p in range(2,pages+1):
                all_albums_urls += get_all_page_albums(browse_letter, page=str(p))
        wait_a_sec()

    #Visit each album page and scrape the media info and audio tracks from it
    for index, album in enumerate(all_albums_urls, start=1):
        print(f"{index}. {album}", end='  ')
        album_url = base_browse_url.replace('browse','album') + album
        page_album_data(album_url)
        print("Done!")
        wait_a_sec()

    #Write all data to a JSON file
    with open('../Data/khi_data.json', 'w') as file:
        file.write(json.dumps(data, indent=4))


def main():
    scrape_all_khi()


if __name__ == "__main__":
    main()
