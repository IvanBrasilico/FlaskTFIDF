# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 20:54:36 2017

@author: ivan https://github.com/IvanBrasilico/
"""
from collections import Counter
from sqlalchemy.orm import sessionmaker
from wordcloud import WordCloud
from models.models import engine, Collection
from models.collectionmanager import CollectionManager

Session = sessionmaker(bind=engine)
session = Session()

teccollection = session.query(Collection).filter_by(id=1).one()

manager = CollectionManager(session, teccollection)

print("Collection lenght: "+str(manager.collection_lenght()))
print("Average Document Length: "+str(manager.avg_dl()))
frequencies = manager.word_frequency_dict()
wordcloud = WordCloud(max_font_size=40, width=800,
                      height=500).generate_from_frequencies(frequencies)
image = wordcloud.to_image()
image.show()

# image.show()

counter = Counter(frequencies)
stats = counter.most_common()
maxcount = stats[0][1]
mincount = stats[-1][1]
print(stats)
print(maxcount)
print(mincount)
main_frequencies = {k: v for
                    k, v in frequencies.items() if (v > 5) and (v < 200)}

wordcloud = WordCloud(max_font_size=40, width=800,
                      height=500).generate_from_frequencies(main_frequencies)
image = wordcloud.to_image()

image.show()
