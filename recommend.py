#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 19:21:57 2020

@author: tatianatian
"""
import pandas as pd
from pymongo import MongoClient
import pymongo
from surprise import Dataset
from surprise import Reader
from surprise import KNNWithMeans
import numpy as np
from operator import itemgetter 


def request_mongo_data():
    mongo_uri = 'mongodb+srv://tatiana:tatiana0824@cluster0.cigjb.mongodb.net/UserInfo?retryWrites=true&w=majority'
    conn = MongoClient(mongo_uri)
    
    reviews = conn['UserInfo']['reviews'].find()
    profile = conn['UserInfo']['users'].find()

    reviews_df = pd.DataFrame(list(reviews))
    profile_df = pd.DataFrame(list(profile))
    
    reviews_df = reviews_df[['restaurantId','userId','review']]
    profile_df = profile_df[['_id','zip_code','age','kids','relationship','veg','religion']]
    
    reviews_df = reviews_df.astype('string')
    
    return [reviews_df,profile_df]


def stringToList(string):
    res_list = []
    pos = 0
    count = 0
    for i in range(len(string)):
        if string[i]=="'" and count == 1:
            print(i)
            res_list.append(string[pos+1:i])
            count = 0
        elif string[i]=="'" and count == 0:
            pos = i
            count = 1
    return res_list
    

def recommend(userId, restaurant_list, reviewCountCut, topN):
    
    restaurant_list = stringToList(restaurant_list)
    [reviews_df,profile_df] = request_mongo_data()
    
    # check if the user reviews 3 stores:
    user_review = reviews_df[reviews_df['userId']==userId]
    if user_review.shape[0] > reviewCountCut:
        
        # prepare data
        reviews_np = reviews_df.to_numpy()

        item = []
        user = []
        rating = []

        for i in range(len(reviews_np)):
            item.append(reviews_np[i][0])
            user.append(reviews_np[i][1])
            rating.append(reviews_np[i][2])
            
        review_ratings_dict={
            "item": item,
            "user": user,
            "rating": rating,
        }

        df = pd.DataFrame(review_ratings_dict)
        reader = Reader(rating_scale=(1, 3))
        data = Dataset.load_from_df(df[["user", "item", "rating"]], reader)

        # To use user-based pearson similarity
        sim_options = {
            "name": "pearson",
            "user_based": True,  # Compute  similarities between users
        }
        algo = KNNWithMeans(sim_options=sim_options)

        trainingSet = data.build_full_trainset()
        algo.fit(trainingSet)

        # Predict
        rating_dict = {}

        for i in range(len(restaurant_list)):
            est_rating = algo.predict(userId, restaurant_list[i]).est
            rating_dict[restaurant_list[i]] = est_rating

        rating_dict = {k: v for k, v in sorted(rating_dict.items(), key=lambda item: item[0])}
        res = dict(sorted(rating_dict.items(), key = itemgetter(1), reverse = True)[:topN])
        
        return list(res.keys())
    
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    