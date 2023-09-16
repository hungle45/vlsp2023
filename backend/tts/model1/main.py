import torch
import torchaudio

class Model:
    def syn(self, text: str, emotion: int):
        return torchaudio.load('./tts/dummy.wav')[0]