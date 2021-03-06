import re
import random
from pycantus.pycantus import Cantus
from pycantus.pycantus.volpiano import volpiano_characters, add_flats, volpiano_to_midi
from collections import defaultdict
from plotting import *
import pickle

_DATASET_PATH = "../data/chantdata.pickle"

flatten_list = lambda l: [item for sublist in l for item in sublist]
clean_volpiano = lambda volpiano, reg: re.sub(reg, '', volpiano)

valid_characters = volpiano_characters('liquescents', 'naturals', 'flats', 'notes')
clean_regex = f"[^{valid_characters}-]+"

class ChantData(object):
    def __init__(self, volpiano, mode):
        self.mode = mode
        self.pitch_separated = volpiano
        self.pitch = volpiano.replace("-", "")
        #self.midi_separated = volpiano_to_midi(self.pitch_separated)
        self.midi = volpiano_to_midi(self.pitch)
        self.interval = [midi_pitch - self.midi[0] for midi_pitch in self.midi]
        self.contour = flatten_list([[midi_pitch - volpiano_to_midi(group)[0] for midi_pitch in volpiano_to_midi(group)] for group in self.pitch_separated.split("-") if group])

    def get_size(self, input_level):
        return len(getattr(self, input_level))

class ChantDataset(object):
    def __init__(self, input_level="midi"):
        self.input_level = input_level

        pre_data = self.load_data()
        self.data = self.filter_data(pre_data)
        self.pad_size = self.find_pad_size()

        self.train_data, self.train_y, self.valid_data, self.valid_y, self.test_data, self.test_y = self.split_dataset()

    @staticmethod
    def load_data():
        try:
            cdata = pickle.load(open(_DATASET_PATH, "rb"))
        except (OSError, IOError) as e:
            print(e)
            cdata = []
            PyCantusUtil()
            data_pyc = PyCantusUtil.build_dataset()
            for chant, mode in data_pyc:
                cdata.append(ChantData(chant, mode))
            pickle.dump(cdata, open(_DATASET_PATH, "wb"))
        finally:
            return cdata

    def filter_data(self, data):
        return [d for d in data if 5 <= d.get_size(self.input_level) <= 200]

    def split_data_label(self, dataset):
        data = [getattr(chant, self.input_level) for chant in dataset]
        label = [chant.mode for chant in dataset]

        return data, label

    def split_dataset(self, validation_data=False, train_slice=0.8):
        random.seed(42)
        random.shuffle(self.data)

        train = self.data[: int(len(self.data) * train_slice)]
        test = self.data[int(len(self.data) * train_slice):]

        if validation_data:
            valid = test[: len(test) // 2]
            test = test[len(test) // 2:]
        else:
            valid = []

        train.sort(key=lambda chant: chant.get_size(self.input_level))

        train_data, train_y = self.split_data_label(train)
        test_data, test_y = self.split_data_label(test)
        valid_data, valid_y = self.split_data_label(valid)

        return (train_data, train_y,
                valid_data, valid_y,
                test_data, test_y)

    def find_pad_size(self):
        max_size = max([d.get_size(self.input_level) for d in self.data])
        return max_size

    def set_input_level(self, input_level):
        self.input_level = input_level
        self.train_data, self.train_y, self.valid_data, self.valid_y, self.test_data, self.test_y = self.split_dataset()
        self.pad_size = self.find_pad_size()



class PyCantusUtil(object):
    def __init__(self):
        Cantus.load()

    @staticmethod
    def get_valid_chants():
        chants = Cantus.chants[Cantus.chants.volpiano.notnull()]
        chants = chants[chants['mode'].notnull()]
        return chants

    @staticmethod # not used -- will be removed
    def get_chant(chant_index):
        chant = Cantus.get_chant(chant_index)
        mode = chant.mode

        neumes = flatten_list([syllable.neumes for section in chant.parsed_chant.sections if chant.parsed_chant.is_complete for word in section.words for syllable in word.syllables])
        syllables = []
        if neumes:
            syllables = ["".join(syllable.neumes) for section in chant.parsed_chant.sections if chant.parsed_chant.is_complete for word in section.words for syllable in word.syllables if syllable.neumes]
        return neumes, syllables, mode

    @staticmethod
    def get_chant_sections(index):
        chant = Cantus.get_chant(index)

        sections = [section.volpiano for section in chant.parsed_chant.sections]
        mode = chant.mode

        return sections, mode

    @staticmethod
    def is_valid_mode(mode):
        return mode.isdigit()

    @staticmethod
    def parse_section(section):
        section = add_flats(section)
        return clean_volpiano(section, clean_regex).strip("-")

    @staticmethod
    def parse_sections(sections):
        return [p_section for p_section in (PyCantusUtil.parse_section(section) for section in sections if section) if p_section]

    @staticmethod
    def build_dataset():
        chants = PyCantusUtil.get_valid_chants()
        dataset = []

        i = 1
        for index, row in chants.iterrows():
            if i % 1000 == 0:
                print(f"{i} / {chants.shape[0]}")
            i += 1

            sections, mode = PyCantusUtil.get_chant_sections(index)

            if not PyCantusUtil.is_valid_mode(mode):
                continue

            sections = PyCantusUtil.parse_sections(sections)
            for section in sections:
                dataset.append((section, mode))

        return dataset


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
        neumes, syllables, mode = PyCantusUtil.get_chant(index)
        if syllables:
            parsed_neumes = [clean_volpiano(neume, clean_regex).replace("-", "") for neume in neumes]
            parsed_syllables = [clean_volpiano(syllable, clean_regex).replace("-", "") for syllable in syllables]

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

def input_length_histogram(data):
    d = [chant.get_size("midi") for chant in data]

    build_histogram(d, "Input lengths")

data = ChantDataset()
input_length_histogram(data.data)