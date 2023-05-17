import json
import random

import numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans, DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics import silhouette_score, davies_bouldin_score, mutual_info_score
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.manifold import TSNE
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk import PorterStemmer, WordNetLemmatizer
import string as st
import re
from matplotlib import pyplot as plt
from pathlib import Path
import gensim
from gensim.models import LdaModel
from gensim.models import LdaMulticore

DATA_DIR = Path(__file__).parent.parent.parent / 'data'
SEED = 0


def preprocessing(data):
    # stopword removal etc.
    stopwords = nltk.corpus.stopwords.words('english')
    stopwords.extend([str(_) for _ in range(3000)])
    # remove punctuation
    data['abstract'] = data['abstract'].apply(lambda x: ("".join([ch for ch in x if ch not in st.punctuation])))
    # set all letters to lowercase
    data['abstract'] = data['abstract'].apply(lambda msg: [x.lower() for x in re.split('\s+', msg)])
    # remove small words
    data['abstract'] = data['abstract'].apply(lambda x: [y for y in x if len(x) > 3])
    # remove stop words
    data['abstract'] = data['abstract'].apply(lambda x: [word for word in x if word not in stopwords])

    # stemming
    data['abstract_stem_lem'] = data['abstract'].apply(lambda wrd: [PorterStemmer().stem(word) for word in wrd])
    # lemmatize
    data['abstract_stem_lem'] = data['abstract_stem_lem'].apply(lambda x: [WordNetLemmatizer().lemmatize(word) for word in x])

    # join
    data['abstract'] = data['abstract'].apply(lambda x: " ".join([word for word in x]))
    data['abstract_stem_lem'] = data['abstract_stem_lem'].apply(lambda x: " ".join([word for word in x]))

    return data


def tf_idf(docs):
    tfidfvectorizer = TfidfVectorizer()
    tfidf_vect = tfidfvectorizer.fit_transform(docs['abstract_stem_lem'])

    # create df with tf idf values
    column_names = tfidfvectorizer.vocabulary_.keys()
    data = tfidf_vect.todense()

    df = pd.DataFrame(data=data, columns=column_names, index=range(data.shape[0]))

    dist_mat = cosine_similarity(tfidf_vect)

    return df, dist_mat


def clustering(distances: np.ndarray, features):

    # adapt dist_matrix -> delete rows with just zeros (no abstract) + corresponding columns
    # => keep indices to assign cluster results properly
    idx_to_keep = []
    idx_to_del = []

    for i, doc in enumerate(distances):
        if np.sum(doc) == 0:
            idx_to_del.append(i)
        else:
            idx_to_keep.append(i)

    distances = np.delete(np.delete(distances, idx_to_del, 1), idx_to_del, 0)
    scores = []
    label_list = []

    for n in range(2, distances.shape[0]):
        clustering = AgglomerativeClustering(n_clusters=n, affinity='cosine', linkage='average')
        labels = clustering.fit_predict(distances)

        # kmeans = KMeans(n_clusters=n, init='random', n_init=10, max_iter=300)
        # labels = kmeans.fit_predict(distances)
        label_list.append(labels)

        # print score
        ss = silhouette_score(features.values, labels)
        scores.append(ss)
    index = np.argsort(scores)[-1]
    print(f"Best result for {index} cluster with a score of {scores[index]}")

    return label_list[index]


def get_topic(docs, n_components=2):

    # let's do a countvectorizer now
    count_vectorizer = CountVectorizer()
    X = count_vectorizer.fit_transform(docs['abstract'])

    # we are only creating 2 topics
    lda = LatentDirichletAllocation(n_components=n_components, random_state=0)
    lda.fit(X)
    feature_names = count_vectorizer.get_feature_names_out()
    topic_label = []
    for topic_id, topic in enumerate(lda.components_):
        print(f"Topic {topic_id}:")
        label = " ".join([feature_names[i] for i in topic.argsort()[:-6:-1]])
        topic_label.append(label)
        print(label)

    assigned_topic_list = []
    assigned_prob_list = []

    # get distances between all abstracts and topics
    topic_dists = np.zeros((len(relevant_data.index.values), n_components))
    for i, abstract_vector in enumerate(X.todense()):
        topic_distribution = lda.transform(abstract_vector)
        assigned_prob = 0
        assigned_topic = None
        for topic_idx, topic_prob in enumerate(topic_distribution[0]):
            topic_dists[i][topic_idx] = topic_prob
            # assign new prob if greater than current + assign topic index
            if topic_prob > assigned_prob:
                assigned_prob = topic_prob
                assigned_topic = topic_idx
        # append topic + prob for current paper
        assigned_prob_list.append(assigned_prob)
        assigned_topic_list.append(assigned_topic)

    # evaluation

    preprocessed_documents = []
    for document in docs:
        tokens = count_vectorizer.get_feature_names_out()
        preprocessed_documents.append(tokens)

    # print(tokens)

    dictionary = gensim.corpora.Dictionary(preprocessed_documents)
    corpus = [dictionary.doc2bow(doc) for doc in preprocessed_documents]

    lda_model = gensim.models.LdaModel(corpus=corpus, num_topics=2, id2word=dictionary, passes=10)
    coherence_model = gensim.models.CoherenceModel(model=lda_model, texts=preprocessed_documents, dictionary=dictionary,
                                                   coherence='c_v')
    coherence_score = coherence_model.get_coherence()
    print(f"Coherence score: {coherence_score:.2f}")

    return topic_dists, topic_label, assigned_topic_list, assigned_prob_list


if __name__ == "__main__":

    np.random.seed(SEED)
    random.seed(SEED)

    with open(DATA_DIR / 'extracted.json', 'r') as handle:
        input_data = pd.read_json(handle)

    final_df = pd.DataFrame({'title': input_data.title.values})

    relevant_data = input_data[input_data.abstract != ''].copy()

    prepared_data = preprocessing(relevant_data)

    # clustering
    vectors, dist_matrix = tf_idf(prepared_data)

    cluster = clustering(dist_matrix, vectors)
    data_out = pd.DataFrame({'cluster': cluster}, index=relevant_data.index.values)

    # visualize clustering
    data_emb = TSNE(n_components=2, learning_rate='auto', init='random', perplexity=3).fit_transform(vectors.values)
    data_emb = np.array(data_emb)
    plt.scatter(data_emb[:, 0], data_emb[:, 1], c=cluster)
    plt.title('embeddings for tf-idf paper vectors')
    # plt.show()

    # topics
    # set range if you want to sweep over different n
    for n in [7]:
        topic_distances, topic_labels, assigned_topics, assigned_probs = get_topic(relevant_data, n)

    # add topic distances to relevant data
    for i in range(topic_distances.shape[1]):
        data_out[f"distance_to_topic_{i}"] = topic_distances[:, i]

    # append assigned topic + assigned probs to df
    data_out['topic_id'] = assigned_topics
    data_out['topic_prob'] = assigned_probs
    data_out['topic'] = [topic_labels[i] for i in assigned_topics]

    # add relevant data to final -> NaN for the documents without abstract
    final_df = pd.concat([final_df, data_out], axis=1)
    final_df.to_json(DATA_DIR / 'abstract_ai_data.json')

    # code snippet to get topic_id - topic allocation
    unique_df = final_df.drop_duplicates(subset=['topic'])
    unique_df = unique_df.dropna()
    topic_id_allocation = [{'id': topic_id, 'topic': topic} for topic_id, topic in
                           zip(unique_df.topic_id.values, unique_df.topic.values)]
    print(topic_id_allocation)
    with open(DATA_DIR / 'topic_id_list.json', 'w') as handle:
        json.dump(topic_id_allocation, handle)
