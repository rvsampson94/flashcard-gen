import requests
import csv
from bs4 import BeautifulSoup

def generate_audio(word, url):
    url = url.replace('//', 'https://')
    r = requests.get(url)
    # write content to mp3 file
    with open('audio/' + word + '.mp3', 'wb+') as file:
        file.write(r.content)

def extract_reading(tag):
    reading = tag.find('audio').get('id').split(':')[-1]
    audio_src = tag.find('source', {'type': 'audio/mpeg'}).get('src')
    return (reading, audio_src)

def extract_definition(tag):
    return tag.find('span', {'class': 'meaning-meaning'}).text

def extract_kanji_meanings(tag):
    kanji = []
    meanings = []
    kanji_tiles = tag.find_all('div', {'class': 'kanji_light_content'})
    for tile in kanji_tiles:
        char = tile.find('div', {'class': 'literal_block'}).find('span').text
        spans = tile.find('div', {'class': 'meanings english sense'}).find_all('span')
        meaning = ''
        for span in spans:
            meaning += span.text
        kanji.append(char)
        meanings.append(meaning)
    return (kanji, meanings)

in_f_name = 'words.txt'
out_f_name = 'gen.tsv'

with open(in_f_name, 'r') as in_f:
    with open(out_f_name, 'w+') as out_f:
        tsv_writer = csv.writer(out_f, delimiter='\t')
        jisho = 'https://jisho.org/search/'
        for word in in_f:
            word = word.strip()
            print(len(word))
            r = requests.get(jisho + word)
            soup = BeautifulSoup(r.text, features='html.parser')
            exact_block = soup.find('div', {'class', 'exact_block'})
            kanji_block = soup.find('div', {'class', 'kanji_light_block'})
            reading = extract_reading(exact_block)
            definition = extract_definition(exact_block)
            kanji = extract_kanji_meanings(kanji_block)
            line = [
                word + '[' + reading[0] + ']',
                definition,
                ';'.join(kanji[0]),
                ';'.join(kanji[1])
            ]
            tsv_writer.writerow(line)
            generate_audio(word, reading[1])
            