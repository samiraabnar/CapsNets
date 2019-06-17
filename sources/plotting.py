from matplotlib import pyplot as plt
import seaborn as sns


# input: dict(dict(int)), string
def barplot_frequencies(freq_dict, title):
    modes, freqs = [*zip(*freq_dict.items())]

    plt.boxplot(freqs)
    plt.xticks(range(1, len(modes) + 1), modes)
    plt.xlabel("Mode")
    plt.ylabel("Input Length")
    plt.suptitle(title)
    plt.show()


# input: dict(int), string
def build_histogram(freq_list, title):
    sns.distplot(freq_list).set_title(title)
    plt.show()