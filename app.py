import streamlit as st
import pandas as pd
import requests
import pickle

# Load the processed data and similarity matrix
with open('movie_data.pkl', 'rb') as file:
    movies, cosine_sim = pickle.load(file)

def get_recommendations(title, cosine_sim=cosine_sim):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  # Get top 10 similar movies
    movie_indices = [i[0] for i in sim_scores]
    return movies[['title', 'movie_id']].iloc[movie_indices]

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
    sim_scores = sim_scores[1:]  # Exclude the movie itself
    movie_indices = [i[0] for i in sim_scores]
    return movies[['title', 'movie_id', 'overview']].iloc[movie_indices]

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
logo_col, title_col = st.columns([1, 6])
with logo_col:
    st.image("Cinematchlogo.png", width=80)
with title_col:
    st.markdown(
        """
        <div style="margin-bottom: 0.5rem;">
            <h1 style="margin:0;">CineMatch</h1>
            <p style="margin:0; color:#6c757d;">Smart movie recommendations powered by AI</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Sidebar options
st.sidebar.header("Options")
n_rec = st.sidebar.slider("Number of recommendations", 1, 20, 10)

selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button('Recommend'):
    recommendations = get_recommendations(selected_movie)
    st.write("Top recommendations with available posters:")

    # Collect recommendations that have valid posters
    recommendations = recommendations.reset_index(drop=True)
    valid = []
    for _, row in recommendations.iterrows():
        movie_id = row['movie_id']
        poster_url = fetch_poster(movie_id)
        if poster_url:
            valid.append({
                'title': row['title'],
                'movie_id': movie_id,
                'overview': row.get('overview', ''),
                'poster': poster_url,
            })
        if len(valid) >= n_rec:
            break

    if not valid:
        st.warning("No posters available for the recommended movies.")
    else:
        per_row = 5
        for i in range(0, len(valid), per_row):
            cols = st.columns(per_row)
            for col, item in zip(cols, valid[i:i+per_row]):
                with col:
                    try:
                        st.image(item['poster'], use_column_width=True)
                    except Exception:
                        st.info("📷 Poster unavailable")
                    st.markdown(f"**{item['title']}**")
                    if item.get('overview'):
                        with st.expander("Overview"):
                            st.write(item['overview'])
                    tmdb_link = f"https://www.themoviedb.org/movie/{item['movie_id']}"
                    st.markdown(f"[View on TMDB]({tmdb_link})")
