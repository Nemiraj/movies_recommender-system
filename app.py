import streamlit as st
import pickle
import pandas as pd
import requests

# Cache the API calls to improve performance
@st.cache_data
def fetch_poster(movie_id):
    """Fetch the movie poster from TMDb API"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=05d60a505958aa5d6f7f07b7ad2b40b4"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    
    return "https://via.placeholder.com/150?text=No+Image"

def recommend(movie):
    """Fetch recommended movies and their posters"""
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_posters = []

        for i in movie_list:
            movie_id = movies.iloc[i[0]].movie_id  # Ensure movie_id exists
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_posters.append(fetch_poster(movie_id))
        
        return recommended_movies, recommended_posters
    
    except IndexError:
        return [], []

# Load preprocessed data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit UI
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox(
    "🔎 Select a movie:",
    movies['title'].values
)

if st.button("🎥 Recommend Movies"):
    with st.spinner("Fetching recommendations..."):
        names, posters = recommend(selected_movie)

    if names:
        st.subheader("📌 Recommended Movies for You")
        cols = st.columns(5)  # Creates 5 responsive columns
        for col, name, poster in zip(cols, names, posters):
            with col:
                st.image(poster, width=140)
                st.write(f"**{name}**")  # Bold movie title
    else:
        st.error("⚠️ No recommendations found. Try another movie!")
