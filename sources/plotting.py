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
def build_histogram(freq_dict, title):
    plt.bar(range(len(freq_dict)), list(freq_dict.values()), align='center')
    plt.xticks(range(len(freq_dict)), list(freq_dict.keys()))
    plt.show()