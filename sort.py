import pandas as pd

from indicnlp import common, loader
from indicnlp.tokenize import indic_tokenize
from indicnlp.morph.unsupervised_morph import UnsupervisedMorphAnalyzer

INDIC_NLP_LIB_HOME = ".venv\Lib\site-packages\indic_nlp_library-0.92.dist-info"
INDIC_NLP_RESOURCES = ".venv\Lib\site-packages\indic_nlp_resources-master"

def lemmatise_marathi_sentences(sentences):
    """
    Takes a list of sentences and returns a list of lists, each sub-list being a list of lemmas.
    """
    common.set_resources_path(INDIC_NLP_RESOURCES)
    
    loader.load()
    lang = 'mr'

    Lemmatizer = UnsupervisedMorphAnalyzer(lang)

    lemmatised_sentences = []
    for sentence in sentences:
        # Tokenise
        tokens = indic_tokenize.trivial_tokenize(sentence, lang)

        # Lemmatise
        lemmatised_sentence = Lemmatizer.morph_analyze_document(tokens)
        lemmatised_sentences.append(lemmatised_sentence)
        print("Sentence Completed")
    return lemmatised_sentences

def sortMarathiCards():
    """
    Gives each Marathi language card a frequency value by which Anki can sort them.
    The frequency value = X + Y, where
                                 X = the number of occurrences of the *least* frequent word in the sentence.
                                 Y = the average number of occurrences of all the words in the sentence.
    
    This has the effect of prioritising sentences that have few rare words and have a high average frequency in a simple manner. This could definitely be improved.
    """
    # Connect to csv
    csv_file_path = './output/mar → eng.csv'

    # Get iterable over all sentences
    original_df = pd.read_csv(csv_file_path, header=None, delimiter='\t')
    marathi_sentences = original_df[1]

    # Lemmatise
    batch_size = 100
    lemmatised_sentences = []
    for i in range(0, len(marathi_sentences), batch_size):
        if i + batch_size > len(marathi_sentences):
            batch_size = len(marathi_sentences) - i
        batch = marathi_sentences[i:i+batch_size]
        lemmatised_sentences.extend(lemmatise_marathi_sentences(batch))
        print(str(((i+batch_size)/len(marathi_sentences)*100) // 1) + "%")

    # Count word frequency using hash table
    freq = dict()
    for sentence_array in lemmatised_sentences:
        for word in sentence_array:
            freq[word] = freq.get(word, 0) + 1 # Add one to count, if it isn't present default to 0


    # Then, go back over and assign each sentence a value based on (lowest frequency + average of frequencies)
    sentence_frequencies = []
    for sentence_array in lemmatised_sentences:
        total = 0
        minimum = float("inf")
        for word in sentence_array:
            word_value = freq[word]
            total += word_value
            if word_value < minimum:
                minimum = word_value
        sentence_value = minimum + (total//len(sentence_array))
        sentence_frequencies.append(sentence_value)

    # Insert the data as a new column in the csv
    original_df[3] = sentence_frequencies
    original_df.to_csv(csv_file_path, index=False, header=False, sep='\t')