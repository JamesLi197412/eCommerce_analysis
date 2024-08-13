import multiprocessing

import gensim.corpora as corpora
import pandas as pd
# LDA evaluation
import pyLDAvis
import pyLDAvis.gensim
import pyLDAvis.gensim_models as gensimvisualize
from gensim.models.coherencemodel import CoherenceModel
from gensim.models.ldamulticore import LdaMulticore


def LDA(words, num_topics):
    # Load the dictionary
    dictionary = corpora.Dictionary(words)
    dictionary.filter_extremes(no_below=2)

    # generate corpus as BoW
    corpus = [dictionary.doc2bow(word) for word in words]
    cores = multiprocessing.cpu_count()

    # train LDA model, use multiple cores to increase the performance
    lda_model = LdaMulticore(corpus=corpus, id2word=dictionary, num_topics=num_topics,
                             workers=cores - 1, chunksize=2000, passes=200, iterations=100)

    # Evaluate models
    coherence_model = CoherenceModel(model=lda_model, texts=words, dictionary=dictionary, coherence='c_v')
    coherence_score = coherence_model.get_coherence()
    print('Coherence Score: {}'.format(coherence_score))

    return lda_model, corpus, dictionary, coherence_score


def topic_visualisation(lda_model, corpus, dictionary):
    # Visualize the topics
    dickens_visual = gensimvisualize.prepare(lda_model, corpus, dictionary, mds='mmds')
    pyLDAvis.save_html(dickens_visual, 'output/model_evaluation/lda.html')
    pyLDAvis.display(dickens_visual)

    return None


def jaccard_similarity(topic_1, topic_2):
    """
        Derives the Jaccard similarity of two topics

        Jaccard similarity:
        - A statistic used for comparing the similarity and diversity of sample sets
        - J(A,B) = (A ∩ B)/(A ∪ B)
        - Goal is low Jaccard scores for coverage of the diverse elements
    """
    intersection = set(topic_1).intersection(set(topic_2))
    union = set(topic_1).union(set(topic_2))

    return float(len(intersection)) / float(len(union))


def format_topics_sentences(lda_model, corpus, data):
    sent_topics_df = pd.DataFrame()
    # Get main topic in each document
    for i, row in enumerate(lda_model[corpus]):
        row = sorted(row, key=lambda x: (x[1]), reverse=True)

        # Get the Dominant topic, Perc Contribution and Keywords for each document
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:  # => dominant topic
                wp = lda_model.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                # series = pd.DataFrame([int(topic_num), round(prop_topic,4), topic_keywords],
                #                      columns = ['Dominant_Topic', 'Perc_Contribution','Topic_Keywords']
                # )
                series = [int(topic_num), round(prop_topic, 4), topic_keywords]
                series_df = pd.DataFrame([series], columns=['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords'])

                sent_topics_df = pd.concat([sent_topics_df, series_df], axis=0, ignore_index=True)
            else:
                break

    # Add original text to the end of the output

    sent_topics_df = pd.concat([sent_topics_df, data], axis=1)
    return (sent_topics_df)
