import os
import json
import yaml
from io import BytesIO
from typing import Union

import librosa
import torch
import torchaudio

import attridict

from tts.HiFiGAN.vocoder import Generator
from tts.StyleTTS.text_utils import TextCleaner, phonemize_one_text
from tts.StyleTTS.text_utils_en import TextCleaner
from tts.StyleTTS.model import load_ASR_models, load_F0_models, Munch, build_model


class StyleTTSInference:
    def __init__(self, styletts_config_path):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print('Hosting on {}'.format(self.device))

        # load config
        self.config = yaml.safe_load(open(styletts_config_path))

        # text propressing
        self.text_cleaner = TextCleaner()

        # load HiFi GAN
        HFG_config = self.config.get('HiFiGAN_config', False)
        HFG_path = self.config.get('HiFiGAN_path', False)
        self.hfg = self.load_hfg_checkpoint(HFG_path, HFG_config)

        # load pretrained ASR model
        ASR_config = self.config.get('ASR_config', False)
        ASR_path = self.config.get('ASR_path', False)
        print("Loading text aligner config from'{}'".format(ASR_config))
        self.text_aligner = load_ASR_models(ASR_path, ASR_config)
        print("Complete loading text aligner model.")

        # load pretrained F0 model
        F0_path = self.config.get('F0_path', False)
        print("Loading F0 model from'{}'".format(F0_path))
        self.pitch_extractor = load_F0_models(F0_path)
        print("Complete loading F0 model.")

        # load StyleTTS
        model_params = self.config['model_params']
        model_path = self.config['model_path']
        print("Loading StyleTTS model from'{}'".format(model_path))
        self.model = self.load_model(model_params, model_path)
        print("Complete loading StyleTTS checkpoint.")

        # audio related
        self.sr = self.config.get('sample_rate', 22050)
        self.mean, self.std = -4, 4


    # Load Hifi-GAN
    def load_hfg_checkpoint(self, ckpt_path, config_path):
        assert os.path.isfile(ckpt_path)
        assert os.path.isfile(config_path)

        print("Loading HiFi GAN config from'{}'".format(config_path))
        with open(config_path) as f:
            config = f.read()
        json_config = json.loads(config)
        h = attridict(json_config)
        generator = Generator(h).to(self.device)
        print("Complete loading Hifi GAN config.")

        print("Loading HiFi GAN from'{}'".format(ckpt_path))
        checkpoint_dict = torch.load(ckpt_path, map_location=self.device)

        generator.load_state_dict(checkpoint_dict['generator'])
        generator.eval()
        generator.remove_weight_norm()
        print("Complete loading Hifi GAN checkpoint.")

        return generator

    # Load StyleTTS
    def load_model(self, model_params, model_path):
        model = build_model(Munch(model_params), self.text_aligner, self.pitch_extractor)
        
        params = torch.load(model_path, map_location='cpu')
        params = params['net']
        for key in model:
            if key in params:
                if not "discriminator" in key:
                    print('%s loaded' % key)
                    model[key].load_state_dict(params[key])
        _ = [model[key].eval() for key in model]
        _ = [model[key].to(self.device) for key in model]

        return model

    def to_mel(self, wave):
        return torchaudio.transforms.MelSpectrogram(
            n_mels=80, n_fft=2048, win_length=1200, hop_length=300)(wave)

    def length_to_mask(self, lengths):
        mask = torch.arange(lengths.max()).unsqueeze(0).expand(lengths.shape[0], -1).type_as(lengths)
        mask = torch.gt(mask+1, lengths.unsqueeze(1))
        return mask

    def preprocess(self, wave):
        wave_tensor = torch.from_numpy(wave).float()
        mel_tensor = self.to_mel(wave_tensor)
        mel_tensor = (torch.log(1e-5 + mel_tensor.unsqueeze(0)) - self.mean) / self.std
        return mel_tensor

    def compute_style(self, ref_path):
        wave, sr = librosa.load(ref_path, sr=self.sr)
        audio, index = librosa.effects.trim(wave, top_db=30)
        mel_tensor = self.preprocess(audio).to(self.device)
        try:
            with torch.no_grad():
                ref = self.model.style_encoder(mel_tensor.unsqueeze(1))
            ref_embedding = ref.squeeze(1)
        except Exception as e:
            raise e
        
        return ref_embedding

    def process_text(self, text):
        # phonememes = phonemize_one_text(text)
        tokens = self.text_cleaner(text)
        tokens.insert(0, 0)
        tokens.append(0)
        tokens = torch.LongTensor(tokens).to(self.device).unsqueeze(0)
        
        return tokens

    def __call__(self, text: str, ref_audio: Union[str, BytesIO]):
        with torch.no_grad():
            text_tokens = self.process_text(text)
            ref_style_embedding = self.compute_style(ref_audio)

            input_lengths = torch.LongTensor([text_tokens.shape[-1]]).to(self.device)
            m = self.length_to_mask(input_lengths).to(self.device)
            t_en = self.model.text_encoder(text_tokens, input_lengths, m)

            s = ref_style_embedding.squeeze(1)
            style = s
            
            d = self.model.predictor.text_encoder(t_en, style, input_lengths, m)

            x, _ = self.model.predictor.lstm(d)
            duration = self.model.predictor.duration_proj(x)
            pred_dur = torch.round(duration.squeeze()).clamp(min=1)
            
            pred_aln_trg = torch.zeros(input_lengths, int(pred_dur.sum().data))
            c_frame = 0
            for i in range(pred_aln_trg.size(0)):
                pred_aln_trg[i, c_frame:c_frame + int(pred_dur[i].data)] = 1
                c_frame += int(pred_dur[i].data)

            # encode prosody
            en = (d.transpose(-1, -2) @ pred_aln_trg.unsqueeze(0).to(self.device))
            style = s.expand(en.shape[0], en.shape[1], -1)

            F0_pred, N_pred = self.model.predictor.F0Ntrain(en, s)

            out = self.model.decoder((t_en @ pred_aln_trg.unsqueeze(0).to(self.device)), 
                                    F0_pred, N_pred, ref_style_embedding.squeeze().unsqueeze(0))

            c = out.squeeze()
            y_g_hat = self.hfg(c.unsqueeze(0))
            y_out = y_g_hat.squeeze().cpu().numpy()
        
        return y_out, self.sr
