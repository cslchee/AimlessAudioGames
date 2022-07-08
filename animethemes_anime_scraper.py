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
    with open('Data/oped_anime_data.json', 'r') as file:
        data = json.load(file)
    flip_flop = {}
    for anime in tuple(data.keys()):
        for alt in data[anime]['alt titles']:
            flip_flop[alt] = anime

    #print(json.dumps(flip_flop, indent=4))
    with open('Data/oped_alt_titles_flip_flop.json','w') as file:
        file.write(json.dumps(flip_flop, indent=4))


def scrape_all_anime():
    with open('Data/oped_anime_data.json', 'r') as file:
        data = json.load(file)
    # ANIME   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -
    anime_and_url = {}
    base_url = 'https://animethemes.moe'

    soup = BeautifulSoup(requests.get(base_url+'/anime').text, "html.parser")
    wait_a_sec()

    all_anime = soup.findAll('a', {'class': 'sc-76ad0c61-0 dlzcSE'})
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
        info = [x.strip() for x in soup.find('dl', {'class': 'sc-b64e4bba-0 dcMACx'}).prettify().split('\n') if '>' not in x]
        #using x.text puts all the alt titles into one string with on transition
        data[anime_name]['alt titles'] = info[1:info.index('Premiere')]
        data[anime_name]['date'] = info[info.index('Premiere')+1]
        data[anime_name]['studios'] = info[info.index('Studios')+1:info.index('Links')] if 'Studios' in info else 'NA'
        data[anime_name]['series'] = info[info.index('Series')+1] if 'Series' in info else 'NA'

        vid_divs = soup.findAll('div', {'class': 'sc-47964127-0 sc-95e98e95-0 sc-ff93e959-0 kXAqYY dktsVH fmxeEY'})
        for vid in vid_divs:
            op_ed = 'op' if ('OP' in vid.find('span', {'class': 'sc-76ad0c61-0 sc-ff93e959-2 kbNlyE'}).text) else 'ed'
            try:
                vid_name = vid.find('span',{'class': 'sc-76ad0c61-0 SdTj'}).text
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
                print(f'\t\t{op_ed.upper()}: {vid_name} - {label}  -->  {file_source}')

                data[anime_name][op_ed][vid_name] = {label: v_src}
        with open('Data/oped_anime_data.json', 'w') as file:
            file.write(json.dumps(data, indent=4)) #Write after each series, to back up progress


def main():
    #scrape_all_anime()
    create_alt_title_flip_flip()


if __name__ == "__main__":
    main()
