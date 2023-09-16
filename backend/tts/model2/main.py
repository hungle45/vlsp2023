import torch
import torchaudio

class Model:
    def syn(self, text: str, ref_path: str):
        return torchaudio.load(ref_path)[0]