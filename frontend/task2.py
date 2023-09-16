import requests
import json
import base64


LOGIN_URL = 'http://127.0.0.1:5000/login'
TASK2_URL = 'http://127.0.0.1:5000/tts/task2'
REF_AUDIO = 'audio_ref.wav'

# login
user_info = {
    "email": "user0@gmail.com",
    "password": "user0"
}

login_response = requests.post(url=LOGIN_URL, json=user_info)
try:
    print('Login successful')
    token = login_response.json()['result']['access_token']
    print('Token:', token)
except:
    print('Failed to login')
    
# synth speech
input_data = {
    "input_text": "string"
}
    
files = {
    'ref_audio': (REF_AUDIO, open(REF_AUDIO, 'rb'), 'audio/wav'),
}

headers = {'access_token': token}

response = requests.post(url=TASK2_URL, data=input_data, files=files, headers=headers)
try:
    encoded_audio = response.json()['result']['data']
    audio = base64.b64decode(encoded_audio)
    print('Synth speech successful')
    with open('./output/output_task2.wav', 'wb') as f:
        f.write(audio)
except Exception as e:
    print(e)
    print('Failed to synth speech')
