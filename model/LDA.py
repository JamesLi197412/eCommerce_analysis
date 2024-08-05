import multiprocessing

import gensim.corpora as corpora
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# LDA evaluation
import pyLDAvis
import pyLDAvis.gensim
import pyLDAvis.gensim_models as gensimvisualize
import seaborn as sns
from gensim.models.coherencemodel import CoherenceModel
from gensim.models.ldamulticore import LdaMulticore


def LDA(words, num_topics):
    # Load the dictionary
    dictionary = corpora.Dictionary(words)
    dictionary.filter_extremes(no_below=2)

    # generate corpus as BoW
    corpus = [dictionary.doc2bow(word) for word in words]
    cores = multiprocessing.cpu_count()

    # train LDA model
    lda_model = LdaMulticore(corpus = corpus, id2word= dictionary, num_topics=num_topics,
                             workers = cores - 1, chunksize= 2000,   passes = 200, iterations = 100)

    # Evaluate models
    coherence_model = CoherenceModel(model=lda_model, texts=words, dictionary=dictionary, coherence='c_v')
    coherence_score = coherence_model.get_coherence()
    print('Coherence Score: {}'.format(coherence_score))

    # Visualize the topics
    dickens_visual = gensimvisualize.prepare(lda_model, corpus, dictionary, mds='mmds')
    pyLDAvis.save_html(dickens_visual, 'output/model_evaluation/lda.html')
    pyLDAvis.display(dickens_visual)

    return lda_model, corpus


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

def LDA_running(corpus, dirichlet_dict,coh_sta_diffs):
    # Considering topics 10 - 20 topics
    num_topics = list(range(20))
    num_keywords = 15

    LDA_models = {}
    LDA_topics = {}

    LDA_stability = {}
    for i in range(0, len(num_topics) - 1):
        jaccard_sims = []
        for t1, topic1 in enumerate(LDA_topics[num_topics[i]]):  # pylint: disable=unused-variable
            sims = []
            for t2, topic2 in enumerate(LDA_topics[num_topics[i + 1]]):  # pylint: disable=unused-variable
                sims.append(jaccard_similarity(topic1, topic2))

            jaccard_sims.append(sims)

        LDA_stability[num_topics[i]] = jaccard_sims

    mean_stabilities = [np.array(LDA_stability[i]).mean() for i in num_topics[:-1]]

    coherences = [
        CoherenceModel(model=LDA_models[i], texts=corpus, dictionary=dirichlet_dict, coherence='c_v').get_coherence() \
        for i in num_topics[:-1]]

    oh_sta_diffs = [coherences[i] - mean_stabilities[i] for i in
                    range(num_keywords)[:-1]]  # limit topic numbers to the number of keywords
    coh_sta_max = max(coh_sta_diffs)
    coh_sta_max_idxs = [i for i, j in enumerate(coh_sta_diffs) if j == coh_sta_max]
    ideal_topic_num_index = coh_sta_max_idxs[0]  # choose less topics in case there's more than one max
    ideal_topic_num = num_topics[ideal_topic_num_index]

    # Visualisation on
    plt.figure(figsize=(20, 10))
    ax = sns.lineplot(x=num_topics[:-1], y=mean_stabilities, label='Average Topic Overlap')
    ax = sns.lineplot(x=num_topics[:-1], y=coherences, label='Topic Coherence')

    ax.axvline(x=ideal_topic_num, label='Ideal Number of Topics', color='black')
    ax.axvspan(xmin=ideal_topic_num - 1, xmax=ideal_topic_num + 1, alpha=0.5, facecolor='grey')

    y_max = max(max(mean_stabilities), max(coherences)) + (0.10 * max(max(mean_stabilities), max(coherences)))
    ax.set_ylim([0, y_max])
    ax.set_xlim([1, num_topics[-1] - 1])

    ax.axes.set_title('Model Metrics per Number of Topics', fontsize=25)
    ax.set_ylabel('Metric Level', fontsize=20)
    ax.set_xlabel('Number of Topics', fontsize=20)
    plt.legend(fontsize=20)
    plt.show()

    return None


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
