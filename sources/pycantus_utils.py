import re
import pandas as pd
from pycantus.pycantus import Cantus
from pycantus.pycantus.volpiano import volpiano_characters
from matplotlib import pyplot as plt
from collections import defaultdict

flatten_list = lambda l: [item for sublist in l for item in sublist]
clean_neume = lambda c, reg: [re.sub(reg, '', neume) for neume in c]

class ChantData(object):
    def __init__(self):
        Cantus.load()

    @staticmethod
    def get_valid_chants():
        chants = Cantus.chants[Cantus.chants.volpiano.notnull()]
        chants = chants[chants['mode'].notnull()]
        return chants

    @staticmethod
    def get_chant(chant_index):
        chant = Cantus.get_chant(chant_index)
        mode = chant.mode
        neumes = flatten_list([syllable.neumes for section in chant.parsed_chant.sections if chant.parsed_chant.is_complete for word in section.words for syllable in word.syllables])
        syllables = []
        if neumes:
            syllables = ["".join(syllable.neumes) for section in chant.parsed_chant.sections if chant.parsed_chant.is_complete for word in section.words for syllable in word.syllables if syllable.neumes]
        return neumes, syllables, mode


def build_mode_histograms(chant_data):
    notes_hist = defaultdict(lambda: defaultdict(int))
    neumes_hist = defaultdict(lambda: defaultdict(int))
    syllables_hist = defaultdict(lambda: defaultdict(int))

    notes_freq = defaultdict(list)
    neume_freq = defaultdict(list)
    syllable_freq = defaultdict(list)

    mode_freq = defaultdict(int)

    valid_characters = volpiano_characters('liquescents', 'naturals', 'flats', 'notes')
    clean_regex = f"[^{valid_characters}]+"
    i = 1
    for index, row in chant_data.iterrows():
        if i % 1000 == 0:
            print(f"{i} / {chant_data.shape[0]}")
            #break
        neumes, syllables, mode = data.get_chant(index)
        if syllables:
            parsed_neumes = clean_neume(neumes, clean_regex)
            parsed_syllables = clean_neume(syllables, clean_regex)

            notes_freq[mode].append(sum([len(n) for n in parsed_neumes]))
            neume_freq[mode].append(len(neumes))
            syllable_freq[mode].append(len(syllables))

            mode_freq[mode] += 1

            for syllable in parsed_syllables:
                syllables_hist[mode][syllable] += 1
            for neume in parsed_neumes:
                neumes_hist[mode][neume] += 1
                for note in neume:
                    notes_hist[mode][note] += 1
        i += 1

    barplot_frequencies(notes_freq, "Input length -- Note Level")
    barplot_frequencies(neume_freq, "Input length -- Neume Level")
    barplot_frequencies(syllable_freq, "Input length -- Syllable Level")

    build_histogram(mode_freq, "Mode Distribution")

    return notes_hist, neumes_hist, syllables_hist


def barplot_frequencies(freq_dict, title):
    modes, freqs = [*zip(*freq_dict.items())]

    plt.boxplot(freqs)
    plt.xticks(range(1, len(modes) + 1), modes)
    plt.xlabel("Mode")
    plt.ylabel("Input Length")
    plt.suptitle(title)
    plt.show()


def build_histogram(freq_dict, title)

data = ChantData()
chants = data.get_valid_chants()
notes_hist, neumes_hist, syllables_hist = build_mode_histograms(chants)




print(neumes_hist)
plt.bar(notes_hist.keys(), notes_hist.values())
plt.show()


