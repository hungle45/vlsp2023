import re

from phonemizer import phonemize
from phonemizer.separator import Separator

import pandas as pd

class TextCleaner:
    def __init__(self, word_index_dict_path):
        self.word_index_dictionary = self.load_dictionary(word_index_dict_path)

    def __call__(self, text):
        indexes = []
        for char in text:
            try:
                indexes.append(self.word_index_dictionary[char])
            except KeyError:
                print(char)
        return indexes
    
    def load_dictionary(self, path):
        csv = pd.read_csv(path, header=None).values
        word_index_dict = {word: index for word, index in csv}
        return word_index_dict


def phonemize_one_text(text):
    """
    Input: str
    Output: List[token]
    """
    def handle_multilanguage(text):
        pattern1 = r'\([a-zA-Z]+\)(.*?)\([a-zA-Z]+\)'
        pattern2 = r'(.+)\([a-zA-Z]+\)'
        pattern3 = r'\([a-zA-Z]+\)(.+)'

        match1 = re.search(pattern1, text)
        if match1:
            text = match1.group(1)
        else:
            match2 = re.search(pattern2, text)
            match3 = re.search(pattern3, text)
            if match2:
                text = match2.group(1)
            elif match3:
                text = match3.group(1)

        return text.strip()

    def postprocessing(text):
        words = text.split('|')

        output_phonemes = []
        for word in words:
            word = handle_multilanguage(word)
            output_phonemes = output_phonemes + word.split(' ')
        return ' '.join(output_phonemes)

    def intersperse(lst, item):
        result = [None, item] * len(lst)
        result[0::2] = lst
        return result

    phonemizeds = phonemize(
        text,
        language='vi',
        backend='espeak',
        separator=Separator(phone=' ', word='|', syllable='#'),
        strip=True,
        preserve_punctuation=True,
        njobs=4)
    
    phonemizeds = postprocessing(phonemizeds)
    phonemizeds = intersperse(phonemizeds.split(), ' ')

    return phonemizeds