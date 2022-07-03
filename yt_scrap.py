"""Documentation: https://scrapetube.readthedocs.io/en/latest/"""
import scrapetube
import json

def add_playlist_for_openings_or_endings(playlist_id: str, op_or_ed: str):
    if op_or_ed == 'openings' or op_or_ed == 'opening':
        add_playlist(playlist_id, mode='openings')
    elif op_or_ed == 'openings' or op_or_ed == 'ending':
        add_playlist(playlist_id, mode='endings')
    else:
        print("~~Please choose either an opening or an ending.")
        return

def add_playlist(playlist_id: str, mode=None):
    if mode is None or mode not in ('openings','endings'):
        raise ValueError("Mode not set or was set incorrectly. Please choose either openings or endings.")
    if len(playlist_id) != 34:
        raise ValueError("Invalid playlist_id length. It must be exactly 34 characters.")

    print(f"{'- '*15}\nAdding '{mode}' from playlist: https://www.youtube.com/playlist?list={playlist_id}\n{'- '*15}")

    with open('data.json','r') as file:
        data_dict = json.load(file)

    videos = scrapetube.get_playlist(playlist_id)
    existing_ids = tuple([s['id'] for s in data_dict[mode]])
    added_new = 0
    for count, video in enumerate(videos, start=1):
        if video['videoId'] not in existing_ids:
            added_new += 1
            data_dict[mode].append({
                "title": video['title']['runs'][0]['text'],
                "id": video['videoId'],
                "length": int(video['lengthSeconds']),
                # TODO placeholder ideas - Different scrape tool?
                "audio_starts_at": 0,
                "difficulty": 0,
                "view_count": 0,
                "genre": [],
                "artist": ""
            })
        print(f"{count}. {video['title']['runs'][0]['text']}  -->  https://www.youtube.com/watch?v={video['videoId']}")

    print(f"\n~~Added {added_new} entries")
    #print(json.dumps(data_dict, indent=4))
    if added_new > 0:
        with open('data.json', "w") as file:
            file.write(json.dumps(data_dict, indent=4))


#TODO This seems useful --> https://animethemes.moe/

def main():
    #add_playlist("PLEWxb4I8sM9IANpBRkCH-c7fL6sIAq-Ql", mode='openings')
    add_playlist("PLxrsFcLqv7awg11eFfmZSArdQl-eJJKFE", mode='endings')


if __name__ == "__main__":
    main()
