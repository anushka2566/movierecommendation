# Archived copy of Movie-Recommendation-System/app.py
import streamlit as st
import pandas as pd
import requests
import pickle

# Load the processed data and similarity matrix
with open('movie_data.pkl', 'rb') as file:
    movies, cosine_sim = pickle.load(file)

# Function to get movie recommendations
def get_recommendations(title, cosine_sim=cosine_sim):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  # Get top 10 similar movies
    movie_indices = [i[0] for i in sim_scores]
    return movies[['title', 'movie_id']].iloc[movie_indices]

# Cache poster fetching to avoid repeated API calls
@st.cache_data(ttl=3600)
def fetch_poster(movie_id):
    api_key = '7b995d3c6fd91a2284b4ad8cb390c7b8'  # Replace with your TMDB API key
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster for movie {movie_id}: {e}")
        return None

# Streamlit UI
st.markdown(
    """
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="font-size:2.5rem;">🎬</div>
        <div>
            <h1 style="margin:0;">Cinematch AI</h1>
            <p style="margin:0; color:#6c757d;">Smart movie recommendations powered by AI</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button('Recommend'):
    recommendations = get_recommendations(selected_movie)
    st.write("Top 10 recommended movies:")

    # Create a 2x5 grid layout
    for i in range(0, 10, 5):  # Loop over rows (2 rows, 5 movies each)
        cols = st.columns(5)  # Create 5 columns for each row
        for col, j in zip(cols, range(i, i+5)):
            if j < len(recommendations):
                movie_title = recommendations.iloc[j]['title']
                movie_id = recommendations.iloc[j]['movie_id']
                poster_url = fetch_poster(movie_id)
                with col:
                    if poster_url:
                        try:
                            st.image(poster_url, use_column_width=True)
                        except Exception as e:
                            st.info("📷 Poster unavailable")
                    else:
                        st.info("📷 Poster unavailable")
                    st.write(f"**{movie_title}**")
