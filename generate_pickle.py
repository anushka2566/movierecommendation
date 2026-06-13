import pandas as pd
import numpy as np
import ast
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Read the movies CSV
movies = pd.read_csv('tmdb_5000_movies.csv')

# Select relevant columns
movies = movies[['id', 'title', 'overview', 'genres', 'keywords']].copy()
movies.rename(columns={'id': 'movie_id'}, inplace=True)

# Function to convert JSON-like strings to lists
def convert(obj):
    try:
        L = []
        for i in ast.literal_eval(obj):
            L.append(i['name'])
        return L
    except:
        return []

# Process genres and keywords
movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)

# Create tags by combining genres and keywords
movies['tags'] = movies['genres'] + movies['keywords']
movies['tags'] = movies['tags'].apply(lambda x: " ".join(x))
movies['tags'] = movies['tags'].apply(lambda x: x.lower())

# Create TF-IDF matrix and cosine similarity
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['tags'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Save to pickle file
with open('movie_data.pkl', 'wb') as file:
    pickle.dump((movies, cosine_sim), file)

print("movie_data.pkl created successfully!")
