from dotenv import load_dotenv
import dotenv
import os
import base64
import requests
from requests import post
import json
from django.shortcuts import render, HttpResponse
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class Call:    
    def get_token():
        dotenv_file = os.path.join(".env")
        if os.path.isfile(dotenv_file):
            load_dotenv(dotenv_file)
            client_id = os.getenv("CLIENT_ID")
            client_secret = os.getenv("CLIENT_SECRET")
            
            auth_string = client_id + ":" + client_secret
            auth_bytes = auth_string.encode("utf-8")
            auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

            url = "https://accounts.spotify.com/api/token"
            headers = {
                "Authorization" : "Basic " + auth_base64,
                "Content-Type"  : "application/x-www-form-urlencoded"
            }

            data = {"grant_type" : "client_credentials"}
            result = post(url, headers = headers, data =data)
            json_result = json.loads(result.content)
            token = json_result["access_token"]
            return token
        else:
            return ".env not found"

    def get_song_details(song_name, access_token):
        print("YOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        search_url = "https://api.spotify.com/v1/search/"
        parameters_of_query_string = {
            'q': song_name,
            'type': 'track',
            'limit': 10
        }
        headers = {'Authorization': f'Bearer {access_token}'}
        result = requests.get(search_url, parameters_of_query_string, headers=headers)
        
        if result.status_code == 200:
            track_details = result.json()
            t_id = track_details["tracks"]["items"][0]["id"]
            t_name = track_details["tracks"]["items"][0]["name"]
            artists = track_details["tracks"]["items"][0]["artists"]
            
            print(f"\n\n{t_id}\n<'{t_name}'> by <'{artists[0]['name']}'>")
            return track_details
        else:
            print("******************\n\n",result.status_code)
            return result.status_code

    def get_features(track_id, access_token):
        # Preparing the request to send for audio features
        features_url = f'https://api.spotify.com/v1/audio-features/{track_id}'
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Sending a request and getting a response
        response = requests.get(features_url, headers=headers)
        
        if response.status_code == 200:
            # print("FEATURES YOOOOOO")
            audio_features = response.json()
            # print(audio_features)
            return audio_features
        else:
            # print("NOO Features: ",response)
            pass

    def get_recommendation(limit, seed_track, seed_artist, token):
        Recommendation_EndPoint = 'https://api.spotify.com/v1/recommendations/'
        parameters_of_query_string = {
            'limit':limit,
            'seed_artists': seed_artist,
            'seed_tracks' : seed_track,
        }
        headers = {'Authorization': f'Bearer {token}'}

        result = requests.get(Recommendation_EndPoint, parameters_of_query_string, headers=headers)
        
        if result.status_code == 200:
            Recommendation_list = result.json()
            # print("list",Recommendation_list)            
            return Recommendation_list
        else:
            return result.status_code

    def get_top10(targetFeatures, target_track, _100Features, _100Tracks):

        target_track = json.loads(target_track)
        targetFeatures = json.loads(targetFeatures)
        _100Features = json.loads(_100Features)
        _100Tracks = json.loads(_100Tracks)

        # Convert to DataFrame
        target_track_df = pd.DataFrame([target_track])
        targetFeatures_df = pd.DataFrame([targetFeatures])
        _100Features_df = pd.DataFrame([_100Features])
        _100Tracks_df = pd.DataFrame([_100Tracks])

        dfs = []
        dfs2 = []
        for key, val in _100Features_df.items():
            # print(val[0])  # Append the DataFrame to the list
            dfs.append(dict(val[0]))  # Append the DataFrame to the list

        for key, val in _100Tracks_df.items():
            # print(val[0])  # Append the DataFrame to the list
            dfs2.append(dict(val[0]))  # Append the DataFrame to the list


        # Concatenate DataFrames vertically
        other_Features_df = pd.DataFrame(dfs)
        other_tracks_df = pd.DataFrame(dfs2)

        # target_track_df.to_csv("static/target_track_df.csv", index=False, encoding='utf-8', sep=',')
        # targetFeatures_df.to_csv("static/targetFeatures_df.csv", index=False, encoding='utf-8', sep=',')
        # other_tracks_df.to_csv("static/other_tracks_df.csv", index=False, encoding='utf-8', sep=',')
        # other_Features_df.to_csv("static/other_Features_df.csv", index=False, encoding='utf-8', sep=',')


        # ML MODEL FOR RECOMMENDATION
        # Setting Id as index for both DataFrames
        other_Features_df = other_Features_df.set_index('id')
        targetFeatures_df = targetFeatures_df.set_index('id')

        # Removing unneccesrary features
        useless_features = ['type', 'track_href', 'analysis_url', 'uri']
        other_Features_df.drop(columns=useless_features, inplace=True)
        targetFeatures_df.drop(columns=useless_features, inplace=True)

        # Dropping Null Values
        targetFeatures_df.dropna()
        other_Features_df.dropna()

        # Convert duration from milliseconds to seconds
        other_Features_df['duration_sec'] = other_Features_df['duration_ms'] / 1000
        targetFeatures_df['duration_sec'] = targetFeatures_df['duration_ms'] / 1000

        # Drop the original 'duration_ms' column if needed
        other_Features_df.drop(columns=['duration_ms'], inplace=True)
        targetFeatures_df.drop(columns=['duration_ms'], inplace=True)

        '''
            # The actual model that filtersout top 10 songs out of 100
        '''
        # Calculate cosine similarity between target and other songs
        similarities = cosine_similarity(targetFeatures_df.values.reshape(1, -1), other_Features_df.values)
        # print(similarities)


        # Flatten the similarities array
        similarities = similarities.flatten()

        # Create a new column in other_Features_df to store the similarity scores
        other_Features_df['similarity'] = similarities

        # Sort the dataframe by similarity score in descending order
        other_Features_df = other_Features_df.sort_values(by='similarity', ascending=False)

        # Get the top 10 most similar songs
        top_10_similar_songs = other_Features_df.head(10)

        # Reset the index if needed
        # top_10_similar_songs = top_10_similar_songs.reset_index()
        
        # Index of top 10 songs
        top_10_index = top_10_similar_songs.index
        print(top_10_index)
        return top_10_index
        # Print the top 10 similar songs
        # print(top_10_similar_songs)
