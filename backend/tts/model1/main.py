import torch
import torchaudio

class Model:
    def syn(self, text: str, emotion: int):
        wav, sr = torchaudio.load('./tts/dummy.wav') # tensor
        wav = wav.squeeze().detach().cpu().numpy() # numpy array
        if len(wav.shape) == 2: # multi-channel:
            wav = wav[0]
            wav = wav.squeeze()
        return wav, sr