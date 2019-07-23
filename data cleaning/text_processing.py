import nltk
import math
import re
from nltk.corpus import stopwords
stop_words = stopwords.words('english')

import spacy
# Initialize spacy 'en' model, keeping only tagger component (for efficiency)
nlp = spacy.load('en', disable=['parser', 'ner'])

from nltk.tokenize import TreebankWordTokenizer
_tokenizer = TreebankWordTokenizer()

import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim import parsing

# Enable logging for gensim - optional
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

_stopwords = False
stopwordp = re.compile("^[a-zA-Z]+$", re.I)


mentionFinder = re.compile(r"@[a-z0-9_]{1,15}", re.IGNORECASE)
html_links = re.compile(r'^https?:\/\/.*[\r\n]*')


# remove tags, multiple white spaces, odd characters, html links, @mentions
def initial_cleaning(text):
    # if not data is passed, save time and return empty string
    if text == "":
        return text

    cleanedText = text.replace("><", " ").replace("<", "").replace(">", "")

    # remove multiple white spaces
    cleanedText = parsing.preprocessing.strip_multiple_whitespaces(cleanedText)

    # replace HTML symbols and weird code-tag
    cleanedText = cleanedText.replace("?&#xD;&#xA;&#xD;&#xA;&#xD;&#xA;", "")
    cleanedText = cleanedText.replace("&quot;", "").replace("&#xA;", "").replace("%lld", "")

    # get rid of html links
    cleanedText = re.sub(html_links, '', cleanedText)

    # remove any kind of tags
    cleanedText = parsing.preprocessing.strip_tags(cleanedText)

    # replace @mentions
    cleanedText = mentionFinder.sub('', cleanedText)

    # remove punctuation and single letter words
    cleanedText = parsing.preprocessing.strip_punctuation(cleanedText)
    cleanedText = parsing.preprocessing.strip_short(cleanedText, minsize=2)

    return cleanedText


def stopwords():
    global _stopwords
    if _stopwords == False:
        try:
            _stopwords = set(open("/home/norberteke/PycharmProjects/Thesis/data_cleaning/stop_words").read().splitlines())
        except:
            _stopwords = dict()
        #_stopwords.add("")
        #_stopwords.add("'s")
    return _stopwords


def filter_stopwords(tokens):
    global stopwordp
    sw = stopwords()
    w1 = [x for x in tokens if not (x in sw)]
    return [y for y in w1 if not (None == stopwordp.match(y))]


def tokenize(text, tokenizer=_tokenizer):
    tokens = tokenizer.tokenize(text.lower())
    return tokens


def filter_words_by_frequency(dicts, doc_db, filter_fun):
    newdict = dict()
    newdocs = dict()
    ndocs = dict()
    removedwords = set()
    # count words
    for key, doc in doc_db.iteritems():
        for w in doc:
            ndocs[w] = ndocs.get(w, 0) + 1
    keptwords = dict((x, c) for x, c in ndocs.iteritems() if filter_fun(x, c))
    newmap = dict()
    cnt = 2
    for word, count in keptwords:
        newmap
    # drop the bad words
    for key, doc in doc_db.iteritems():
        ndocs[key] = [w for w in doc if w in keptwords]
    # map the words to new values
    for key, doc in doc_db.iteritems():
        ndocs[key] = [w for w in doc if w in keptwords]
    raise Exception("Not Done Don't Use")


def filter_words_in_only_n_file(dicts, doc_db, n=1):
    ndocs = len(doc_db)
    mincount = n

    def thresh(word, count):
        return (count >= mincount)

    return filter_words_by_frequency(dicts, doc_db, thresh)


def filter_uncommon_word(dicts, doc_db, threshold=0.01):
    ndocs = len(doc_db)
    mincount = max(1, math.ceil(ndocs * threshold))

    def thresh(word, count):
        return (count >= mincount)

    return filter_words_by_frequency(dicts, doc_db, thresh)


def filter_common_word(dicts, doc_db, threshold=0.8):
    ndocs = len(doc_db)
    mincount = max(1, math.ceil(ndocs * threshold))

    def thresh(word, count):
        return (count <= mincount)

    return filter_words_by_frequency(dicts, doc_db, thresh)


def filter_and_uncommon_common_word(dicts, doc_db, lowthreshold=0.01, highthreshold=0.8):
    ndocs = len(doc_db)
    mincount = max(1, math.ceil(ndocs * lowthreshold))
    maxcount = max(1, math.ceil(ndocs * highthreshold))

    def thresh(word, count):
        return (count >= mincount and count <= maxcount)

    return filter_words_by_frequency(dicts, doc_db, thresh)


def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]


def lemmatization(texts, allowed_postags):
    """https://spacy.io/api/annotation"""
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent))
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out

def tags_cleaning(str):
    return str.replace("><", " ").replace("<", "").replace(">", "")


def NLP_processing(fullActivity_str):
    # tokenize text
    tokenized_text = tokenize(fullActivity_str)

    # Build the bigram and trigram models
    bigram = gensim.models.Phrases(tokenized_text, min_count=5, threshold=50)  # higher threshold fewer phrases.
    trigram = gensim.models.Phrases(bigram[tokenized_text], threshold=50)

    # Faster way to get a sentence clubbed as a trigram/bigram
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    trigram_mod = gensim.models.phrases.Phraser(trigram)

    def make_trigrams(texts):
        return [trigram_mod[bigram_mod[doc]] for doc in texts]

    # Remove Stop Words
    data_words_nostops = filter_stopwords(tokenized_text)
    data_words_nostops = remove_stopwords(data_words_nostops)

    # Make Bigrams and Trigram
    data_words_trigrams = make_trigrams(data_words_nostops)

    # Do lemmatization keeping only noun, adj, vb, adv, Proper nuns and interjections
    data_lemmatized = lemmatization(data_words_trigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV', 'PROPN', 'INTJ'])

    flattened_list = [y for x in data_lemmatized for y in x]

    # TO DO: filter common/uncommon words

    fullStr = ' '.join(flattened_list)
    return fullStr







