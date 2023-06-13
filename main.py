import json
import pyttsx3, vosk, pyaudio, requests

tts = pyttsx3.init()
voices = tts.getProperty('voices')
tts.setProperty('voices', 'en')

for voice in voices:
    if voice.name == 'Microsoft David Desktop - English(UnitedStates)':
        tts.setProperty('voice', voice.id)
model = vosk.Model('vosk-model-small-ru-0.4')

record = vosk.KaldiRecognizer(model, 16000)
pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000,
                 input=True, frames_per_buffer=8000)
stream.start_stream()

def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if record.AcceptWaveform(data) and len(data) > 0:
            answer = json.loads(record.Result())
            if answer['text']:
                yield answer['text']

def speak(say):
    tts.say(say)
    tts.runAndWait()

sky = {'☀':'солнечно', '☁':'облачно', '☂':'дождь', '❄':'снег'}
wind = {'↙':'юго-западный', '↘':'юго-восточный', '↗':'северо-восточный',
        '↖':'северо-западный', '↓':'южный', '→':'восточный', '↑':'северный', '←':'западный'}

def Weather():
    req = requests.get('https://wttr.in/Saint-Petersburg?format=2')
    data = req.text
    weather = {}
    for c in data:
        if c in sky.keys():
            weather['на улице'] = sky[c]
    weather['температура'] = data[data.index('🌡️') + 1:data.index('C')]
    weather['ветер'] = wind[data[data.index('C') + 4]]
    weather['скорость'] = data[data.index('C') + 5:data.index('k')]
    return weather

print('Приветствую! Чем могу Вам помочь?')
speak('Приветствую! Чем могу Вам помочь?')

pwd = ''
weather = Weather()
for text in listen():
    if text == 'закрыть':
        quit()
    elif text == 'скажи погоду':
        weather = Weather()
        print(str(weather) + 'километров в час')
        speak(str(weather) + 'километров в час')
    elif text == 'ветер':
        weather = Weather()
        print(weather['ветер'], weather['скорость'])
        speak('ветер сегодня' + weather['ветер'] + 'скорость'
              + weather['скорость'] + 'километров в час')
    elif text == 'что насчёт прогулки':
        weather = Weather()
        if int(weather['температура'][1:-1]) < -15:
            speak('Лучше остаться дома: на улице очень холодно')
            print('Лучше остаться дома: на улице очень холодно')
        elif  int(weather['скорость']) > 20:
           speak('Лучше остаться дома: на улице очень ветренно')
           print('Лучше остаться дома: на улице очень ветренно')
        else:
            speak('Сегодня отличная погода для прогулки!')
            print('Сегодня отличная погода для прогулки!')
    elif text == 'сохранить':
        weather = Weather()
        with open('result.txt', 'w', encoding='utf-8') as f:
            f.write(requests.get('https://wttr.in/Saint-Petersburg?format=2').text)
            speak('Данные о погоде сохранены')
            print('Данные о погоде сохранены')
    else:
        print(text)
