
# -*- coding: utf-8 -*-

import pickle
import streamlit as st

def recommend(movie):
    index = movies[movies['Title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    for i in distances[1:6]:
        recommended_movie_names.append(movies.iloc[i[0]].Title)

    return recommended_movie_names


st.markdown('# End-to-end Content-based Recommendation System')
st.markdown('## for movies (based on imdb data)')
movies = pickle.load(open('movie_list.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))

movie_list = movies['Title'].values
selected_movie = st.selectbox(
    "Type the movie title or select it from the dropdown:",
    movie_list
)


if st.button('Recommend me similar movies!'):
    recommended_movie_names = recommend(selected_movie)
    for i in recommended_movie_names:
        st.subheader(i)
        

