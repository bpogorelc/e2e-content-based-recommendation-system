# -*- coding: utf-8 -*-

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pickle


# Data reading into pandas DataFrame
data = pd.read_excel("imdb_data.xlsx")

# Basic info about the data
data.info()

# We rename some columns
data.rename(columns={'Unnamed: 0': 'movie_id'}, inplace=True)
data.rename(columns={'Movie Name': 'Title'}, inplace=True)

# Prepare a list of textual-data columns without null values
columns=['Title', 'Genre', 'Director', 'Cast', 'Description']

# Double check that those columns don't have nulls
data[columns].isnull().values.any() # no null values

# Function to return the list of concatenated title, director, genre and description column
def get_important_features(data):
    important_features=[]
    for i in range (0, data.shape[0]):
        important_features.append(data['Title'][i]+ ' ' + data['Director'][i]+ ' ' +
                                  data['Genre'][i]+ ' ' + data['Description'][i])
    return important_features


# Saving the concatenated columns as a new feature
data['important_features'] = get_important_features(data)

# We vectorize this feature using TfidfVectorizer to calculate similarity
tfidf = TfidfVectorizer(stop_words='english')
#data['Description'] = data['Description'].fillna('')
tfidf_matrix = tfidf.fit_transform(data['important_features'])
tfidf_matrix.shape

# Generating the cosine similrity matrix
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# We need to write a logic that takes a movie title as input and 
# returns the top 5 most similar movies based on cosine similarity.

 # For this, we can create a function that calculates the similarity
 # score of our input with other movies in the corpus, then sort the 
 # scores in descending order to get the top 5 movies with the 
 # highest similarity scores. Here index 0 is discarded in 
 # sim_scores variable so that the function does not return the 
 # same movie that’s been entered in the input.

indices = pd.Series(data.index, index=data['Title']).drop_duplicates()
#indices['Stillwater']
#sim_scores = list(enumerate(cosine_sim[indices['Stillwater']]))
def get_recommendations(title, cosine_sim=cosine_sim):
    idx = indices[title]
    # Get the pairwise similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_sim[idx]))
    # Sort the movies based on the similarity score
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]
    movie_indices = [i[0] for i in sim_scores]
    # Return the top 5 most similar movies
    movies=data['Title'].iloc[movie_indices]
    id=data['movie_id'].iloc[movie_indices]
    dict={"Movies":movies,"id":id}
    final_df=pd.DataFrame(dict)
    final_df.reset_index(drop=True,inplace=True)
    return final_df

# Test our recommendation engine
get_recommendations('Spider-Man: Far from Home')
#Stillwater
get_recommendations('Stillwater')

data.info()
new = data.drop(columns=['Year of Release','Watch Time','Genre','Movie Rating','Metascore of movie','Director','Cast','Votes','Description'])

pickle.dump(new,open('movie_list.pkl','wb'))
pickle.dump(cosine_sim,open('similarity.pkl','wb'))