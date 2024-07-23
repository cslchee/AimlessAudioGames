"""
 Same logic as 'animethemes_series_scrap', but it EVERYTHING. Skips 'Seasons' page
 TODO Currently not catching a song's author (i.e. SONG NAME  by  BAND). It's all separate HTML elements
"""
import json, requests
from random import uniform
from time import sleep
from bs4 import BeautifulSoup

def wait_a_sec():
    sleep(uniform(0.5, 1.5)) # Easy off DDOS/Banning potential

def create_alt_title_flip_flip():
    with open('../Data/oped_anime_data.json', 'r') as file:
        data = json.load(file)
    flip_flop = {}
    for anime in tuple(data.keys()):
        for alt in data[anime]['alt titles']:
            flip_flop[alt] = anime

    #print(json.dumps(flip_flop, indent=4))
    with open('../Data/oped_alt_titles_flip_flop.json', 'w') as file:
        file.write(json.dumps(flip_flop, indent=4))


def scrape_all_anime():
    with open('../Data/oped_anime_data.json', 'r') as file:
        data = json.load(file)
    # ANIME   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -
    anime_and_url = {}
    base_url = 'https://animethemes.moe'

    soup = BeautifulSoup(requests.get(base_url+'/anime').text, "html.parser")
    wait_a_sec()

    all_anime = soup.findAll('a', {'class': 'sc-d86917e8-0 bVdVPS'}) #This might change!
    if len(all_anime) == 0:
        input("Couldn't find any anime on the main page, the class names have probably changed again!  >_")
        exit()

    for anime in all_anime:
        anime_name = anime.text
        anime_and_url[anime_name] = anime['href']

    for anime_name, anime_url in anime_and_url.items():
        if anime_name in data.keys():
            print(f'"{anime_name}" has already been grabbed.')
            continue

        # ANIME OPENINGS / ENDINGS / DETAILS   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -
        print(f"{'- ' * 20}\n{anime_name}  -  {base_url+anime_url}")
        soup = BeautifulSoup(requests.get(base_url+anime_url).text, "html.parser")
        wait_a_sec()
        data[anime_name] = {
            'alt titles': [],
            'studios': [],
            'series': '',
            'date': '',
            'genres': [],
            'synopsis': '',
            'op': {},
            'ed': {}
        }

        #Get and process the synopsis
        try:
            synopsis = soup.find('p', {'class': 'sc-76ad0c61-0 dQNwzr'}).text
            try:
                synopsis = synopsis[:synopsis.index('(Source')]
            except ValueError as e:
                pass  # Ignore error if there's no source citation
            synopsis = synopsis.replace('\n', ' ').replace('  ', '').strip()
        except AttributeError as e:
            synopsis = 'Not Available'
        data[anime_name]['synopsis'] = synopsis

        # Get date/titles/studios.   Alt Titles -> Premiere -> Series (Optional) -> Studios -> Links
        info = [x.strip() for x in soup.find('dl', {'class': 'sc-93902f8-0 cOHMIw'}).prettify().split('\n') if '>' not in x]
        #using x.text puts all the alt titles into one string with on transition
        data[anime_name]['alt titles'] = info[1:info.index('Premiere')]
        data[anime_name]['date'] = info[info.index('Premiere')+1]
        data[anime_name]['studios'] = info[info.index('Studios')+1:info.index('Links')] if 'Studios' in info else 'NA'
        data[anime_name]['series'] = info[info.index('Series')+1] if 'Series' in info else 'NA'

        #Get AniList Genres - It the classes change: Box of links class, link element class
        sidebar_links = soup.findAll('div', {'class': 'sc-b08d39b6-0 cmkFNw'})[-1].findAll('a', {'class':'sc-d86917e8-0 cLKGBD'})
        anilist_link = ""
        for sb_l in sidebar_links:
            if 'anilist' in sb_l['href']:
                anilist_link = sb_l['href']
                break
        if anilist_link:
            soup_anilist = BeautifulSoup(requests.get(anilist_link).text, "html.parser")
            anilist_info = soup_anilist.findAll('div', {'class': 'data-set data-list'})
            for ani_info in anilist_info:
                section_text = ani_info.findAll('div', {'class': 'type'})[0].text
                if section_text == 'Genres':
                    data[anime_name]['genres'] = [g.text for g in ani_info.findAll('a')]
                    break
        else:
            print("\t\tCould not find an AniList link for this anime.")

        vid_divs = soup.findAll('div', {'class': 'sc-47964127-0 sc-f91d738-0 sc-e475d769-0 epJOQu ldUmdf zxBOP'})
        for vid in vid_divs:
            op_ed = 'op' if ('OP' in vid.find('small', {'class': 'sc-d86917e8-0 gMupXm'}).text) else 'ed'
            try:
                vid_name = vid.find('span',{'class': 'sc-d86917e8-0 hKmOyJ'}).text
                #Add song artist's if there is any
                if len(vid.findAll('small', {'class': 'sc-d86917e8-0 aGhNy'})) != 0: #look for 'by'
                    vid_name += f' by {vid.findAll("a", {"class": "sc-d86917e8-0 hKmOyJ"})[0].text}' #Note the 'a' when looking for the class
            except AttributeError as e:
                vid_name = 'NA'
            vid_sources = [x['href'] for x in vid.findAll('a', {'class': 'sc-aa5e92bc-0 sc-aa5e92bc-2 eJSgxI gWHZqy'})]
            vid_splits = [x for x in vid.prettify().split('\n') if '<svg' in x or '<' not in x]

            #Get 'data-icon="film"' indexes. The text for 'sc-76ad0c61...' episodes label will appear 1 index later
            labels = [vid_splits[count+1].strip() for count, x in enumerate(vid_splits) if 'data-icon="film"' in x]

            # OP/ED Source   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -
            for v_src, label in zip(vid_sources, labels): #First split has 'OP1' label
                if label == '—':
                    label = '---' # \u2014
                soup = BeautifulSoup(requests.get(base_url+v_src).text, "html.parser")
                wait_a_sec()
                file_source = soup.find('video', {'class': 'sc-9cfb0b81-1 ekthvd'})['src']
                file_source = file_source[file_source.index('.moe/')+5:-5] #remove 'https://v.animethemes.moe/' and '.webm'
                print(f'\t\t{op_ed.upper()}: {vid_name} - {label}  -->  {file_source}')
                data[anime_name][op_ed][vid_name] = {label: file_source}

        with open('../Data/oped_anime_data.json', 'w') as file:
            file.write(json.dumps(data, indent=4)) #Write after each series, to back up progress


def main():
    scrape_all_anime()
    #create_alt_title_flip_flip()


if __name__ == "__main__":
    main()
