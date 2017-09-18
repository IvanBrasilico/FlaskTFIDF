from collections import Counter
from wordcloud import WordCloud


def word_cloud_maker(frequencies, filepath, minrange=1, maxrange=0,
                     pmax_font_size=40, pwidth=800, pheight=500):
    """Uses WordCloud class to create a Word Cloud image on disk
    Receives a dict with frequencies, a range, and some parameters for
    WordCloud class. Defines some default values for parameters
    Return the filename or none if no success
    and the max and min range of frequencies"""
    counter = Counter(frequencies)
    stats = counter.most_common()
    maxcount = stats[0][1]
    mincount = stats[-1][1]
    if maxrange == 0:
        maxrange = maxcount
    selected_frequencies = {k: v for
        k, v in frequencies.items() if (v >= minrange) and (v <= maxrange)}

    wordcloud = WordCloud(background_color="white",
                          max_font_size=pmax_font_size, width=pwidth,
                          height=pheight
                          ).generate_from_frequencies(selected_frequencies)

    image = wordcloud.to_image()
    try:
        image.save(filepath)
    except IOError as err:
        print("IO error: {0}".format(err))
        return None
    return filepath, mincount, maxcount
