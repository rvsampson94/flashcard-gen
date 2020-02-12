import requests
import csv
from bs4 import BeautifulSoup
from collections import OrderedDict

def is_kanji(c):
    return ord(c) in range(0x4e00, 0x9fff)

# Open files
in_f_name = 'words.txt'
out_f_name = 'gen.tsv'
with open(in_f_name, 'r') as in_f:
    with open(out_f_name, 'w+') as out_f:
        tsv_writer = csv.writer(out_f, delimiter='\t')
        jisho = 'https://jisho.org/search/'

        # Loop over words in input file
        for word in in_f:
            # Remove new line from word
            word = word.strip()

            # Request Jisho page for word and extract relevant HTML blocks
            r = requests.get(jisho + word)
            soup = BeautifulSoup(r.text, features='html.parser')
            exact_block = soup.find('div', {'class', 'exact_block'})
            kanji_block = soup.find('div', {'class', 'kanji_light_block'})
            if not exact_block:
                print("No match found for word: " + word + "skipping ...")
                continue

            # Create list of kanji in word
            kanji_list = []
            for c in word:
                if is_kanji(c): # Hexadecimal Unicode range for CJK Unified Ideographs
                    kanji_list.append(c)
            # Create map to readings and meanings
            kanji_dict = {}
            for k in kanji_list:
                kanji_dict[k] = {
                    'reading': None,
                    'meaning': None
                }

            if kanji_dict:
                # Get furigana from the exact block and map kanji to readings in dictionary
                furigana_tiles = exact_block.find('span', {'class': 'furigana'}).find_all('span')
                for i, k in enumerate(kanji_dict):
                    kanji_dict[k]['reading'] = furigana_tiles[i].text

                # Iterate through kanji and look for their entry in the kanji block then map meaning to characters
                kanji_tiles = kanji_block.find_all('div', {'class': 'kanji_light_content'})
                for kanji in kanji_dict.keys():
                    for tile in kanji_tiles:
                        char = tile.find('div', {'class': 'literal_block'}).find('span').text
                        if char == kanji:
                            spans = tile.find('div', {'class': 'meanings english sense'}).find_all('span')
                            meaning = ''
                            for span in spans:
                                meaning += span.text
                            kanji_dict[kanji]['meaning'] = meaning
                            break

            # Extract words defintion from exact block
            definition = exact_block.find('span', {'class': 'meaning-meaning'}).text

            # Make audio file if possible
            audio_src = exact_block.find('source', {'type': 'audio/mpeg'})
            if audio_src:
                audio_src = 'https:' + audio_src.get('src')
                r = requests.get(audio_src)
                # write content to mp3 file
                with open('audio/' + word + '.mp3', 'wb+') as file:
                    file.write(r.content)

            # Add furigana to word if needed
            with_furigana = ''
            if kanji_dict:
                for c in word:
                    with_furigana += c
                    if is_kanji(c):
                        with_furigana += '[' + kanji_dict[c]['reading'] + ']'
            else:
                with_furigana = word

            line = [
                with_furigana,
                definition,
                '*'.join(kanji_dict.keys()),
                '*'.join(v['meaning'] for k, v in kanji_dict.items())
            ]
            tsv_writer.writerow(line)
            