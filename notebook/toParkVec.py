
# coding: utf-8

# ## Doc2Vec

# In[11]:

from gensim.models import Doc2Vec
from gensim.models.doc2vec import LabeledSentence


# In[12]:

class LabeledLineSentence(object):
    def __init__(self, filename):
        self.filename = filename
    def __iter__(self):
        for uid, line in enumerate(open(self.filename)):
            yield LabeledSentence(words=line.split(), tags=['TXT_%s' % uid])


# In[ ]:

sentences = LabeledLineSentence('../data/kim.txt')


# In[ ]:

model = Doc2Vec(alpha=0.025, min_alpha=0.001, window=5, min_count=5, dm=1, workers=8, sample=1e-5)


# In[ ]:

model.build_vocab(sentences)


# In[ ]:

for epoch in range(501):
    try:
        model.train(sentences)
        model.alpha *= 0.99
        model.min_alpha = model.alpha
        if not epoch % 100: print ('epoch %d' % (epoch), model.alpha)
    except (KeyboardInterrupt, SystemExit):
        break


# In[ ]:

model.save('../data/kim')

