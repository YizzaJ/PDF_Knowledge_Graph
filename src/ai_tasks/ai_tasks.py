import numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans, DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk import PorterStemmer, WordNetLemmatizer
import string as st
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / 'data'


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


def clustering(distances: np.ndarray):

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

    clustering = AgglomerativeClustering(n_clusters=4, affinity='cosine', linkage='complete')
    labels = clustering.fit_predict(distances)

    # kmeans = KMeans(n_clusters=3, init='random', n_init=10, max_iter=300)
    # labels = kmeans.fit_predict(cos_sim_matrix)

    # dbscan = DBSCAN(eps=0.1, min_samples=2, metric='precomputed')
    # labels = dbscan.fit_predict(cos_sim_matrix)

    # TODO evaluate clustering -> good n? check manually and by distance within clusters

    return labels


def get_topic(docs, n_components=2):

    # let's do a countvectorizer now
    count_vectorizer = CountVectorizer()
    X = count_vectorizer.fit_transform(docs['abstract'])
    # TODO how many topics?? -> according to clusters??
    # we are only creating 2 topics
    lda = LatentDirichletAllocation(n_components=n_components, random_state=0)
    lda.fit(X)
    feature_names = count_vectorizer.get_feature_names_out()
    for topic_id, topic in enumerate(lda.components_):
        print(f"Topic {topic_id}:")
        print(" ".join([feature_names[i] for i in topic.argsort()[:-6:-1]]))

    # get distances between all abstracts and topics
    topic_dists = np.zeros((len(relevant_data.index.values), n_components))
    for i, abstract_vector in enumerate(X.todense()):
        topic_distribution = lda.transform(abstract_vector)
        for topic_idx, topic_prob in enumerate(topic_distribution[0]):
            topic_dists[i][topic_idx] = topic_prob

    return topic_dists


if __name__ == "__main__":
    with open(DATA_DIR / 'papers.json', 'r') as handle:
        input_data = pd.read_json(handle)

    final_df = pd.DataFrame({'title': input_data.title.values})

    relevant_data = input_data[input_data.abstract != ''].copy()

    prepared_data = preprocessing(relevant_data)

    # clustering
    vectors, dist_matrix = tf_idf(prepared_data)

    cluster = clustering(dist_matrix)
    data_out = pd.DataFrame({'cluster': cluster}, index=relevant_data.index.values)

    # topics
    topic_distances = get_topic(relevant_data, 3)

    # add topic distances to relevant data
    for i in range(topic_distances.shape[1]):
        data_out[f"dist_top_{i}"] = topic_distances[:, i]

    # add relevant data to final -> NaN for the documents without abstract
    final_df = pd.concat([final_df, data_out], axis=1)

    final_df.to_json(DATA_DIR / 'abstract_ai_data.json')
