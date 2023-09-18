import io
import soundfile as sf

from typing import Union, Annotated
from enum import IntEnum
import base64


import torchaudio
from decouple import config
from fastapi import APIRouter, Body, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.schemas.users import UserSchema
from core.dependencies import current_user_dependency
from tts import Model1, Model2

# load config
SAMPLE_RATE = int(config('SAMPLE_RATE'))

# load models
tts1 = Model1()
tts2 = Model2()

class Emotions(IntEnum):
    NEUTRAL = 1
    ANGRY = 2
    SAD = 3 
    HAPPY = 4
    

# router
tts_router = APIRouter(tags = ['tts'])
templates = Jinja2Templates(directory="core/views")

@tts_router.get('/tts/task1', response_class=HTMLResponse, include_in_schema=False)
async def task1(request: Request):
    return templates.TemplateResponse('/tts/task1.html', {'request': request})


@tts_router.post('/tts/task1')
async def task1(
    current_user: Annotated[UserSchema, current_user_dependency],
    input_text: Annotated[str, Body()],
    emotion: Annotated[Emotions, Body()]
):
    wav, sr = tts1.syn(input_text, emotion)
    audio_byte = io.BytesIO()
    sf.write(audio_byte, wav, sr, format='wav', subtype='PCM_16')
    encoded_audio = base64.b64encode(audio_byte.getbuffer()).decode('utf-8')

    return {
        'status': 1,
        'input': {
            'text': input_text,
            'emotion': emotion.name
        },
        'result': {
            'data': encoded_audio
        }
    }


@tts_router.get('/tts/task2', response_class=HTMLResponse, include_in_schema=False)
async def task2(request: Request):
    return templates.TemplateResponse('/tts/task2.html', {'request': request})


@tts_router.post('/tts/task2')
async def task2(
    current_user: Annotated[UserSchema, current_user_dependency],
    input_text: Annotated[str, Body()],
    ref_audio: Annotated[UploadFile, File()]
):
    print(ref_audio.filename)
    file_location = f'temp/{ref_audio.filename}'
    wav, sr = tts2.syn(input_text, file_location)
    audio_byte = io.BytesIO()
    sf.write(audio_byte, wav, sr, format='wav', subtype='PCM_16')
    encoded_audio = base64.b64encode(audio_byte.getbuffer()).decode('utf-8')
    
    return {
        'status': 1,
        'input': {
            'text': input_text,
            'filename': ref_audio.filename
        },
        'result': {
            'data': encoded_audio
        }
    }
