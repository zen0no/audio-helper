import json, os

import pyttsx3, vosk, requests
from pyaudio import PyAudio, paInt16 

from PIL import Image
import io
from random import randint

tts = pyttsx3.init()

voices = tts.getProperty('voices')
tts.setProperty('voices', 'en')

for voice in voices:
    print('voice')
    if voice.name == 'Microsoft David Desktop - English (United States)':
        tts.setProperty('voice', voice.id)
        tts.setProperty('rate', 145)

model = vosk.Model('model_small')
record = vosk.KaldiRecognizer(model, 16000)
pa = PyAudio()

stream = pa.open(format=paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8000)

stream.start_stream()


def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if record.AcceptWaveform(data) and len(data) > 0 : 
            answer = json.loads(record.Result())
            if answer['text']:
                yield answer['text']

def speak(say):
    tts.say(say)
    tts.runAndWait()

print('start')

pwd = ''

url_path = 'https://rickandmortyapi.com/api/character/'

count = requests.get(url_path).json()['info']['count']
current_id = 1

def get_image(idx: int): 
    response = requests.get(os.path.join(url_path, 'avatar', f'{current_id}.jpeg')).content
    print(len(response))
    image = Image.open(io.BytesIO(response))
    return image

image = get_image(current_id)

for text in listen():
    if text == 'случайный':
        current_id = randint(1, count)
        response = requests.get(os.path.join(url_path, str(current_id))).json()
        speak(f"his name is {response['name']}")
        image = get_image(current_id)
    if text == 'показать':
        image.show(title=f'{current_id}')

    if text == 'сохранить':
        image.save(os.path.join(os.getcwd(), f'current_id.jpg'))
        speak('saved')
    if text == 'разрешение' or text == 'разрешения':
        speak(f'{image.size[0]} times {image.size[1]} pixels')

    if text == 'эпизод': 
        response = requests.get(os.path.join(url_path, str(current_id))).json()
        speak(f'epise: {response["episode"][0].split("/")[-1]}')
