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
from scipy import stats
import operator


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
    for i in range(len(string)):
        if string[i]==',':
            if (len(res_list) == 0):
                res_list.append(string[:i])
            else:
                res_list.append(string[pos+1:i])
            pos = i
    
    res_list.append(string[pos+1:])
    return res_list
    

def recommend(userId, restaurant_list, reviewCountCut, userCountCut):
    print ('restaurant_list is ')
    print (restaurant_list)
    
    restaurant_list = stringToList(restaurant_list)
    [reviews_df,profile_df] = request_mongo_data()
    
    # check if the user reviews 3 stores:
    user_review = reviews_df[reviews_df['userId']==userId]
    avg_rating = reviews_df["review"].astype('int32').mean()

    
    if user_review.shape[0] >= reviewCountCut:
        print('use review')
        
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
        rec_list = []

        for i in range(len(restaurant_list)):
            est_rating = algo.predict(userId, restaurant_list[i]).est
            rating_dict[restaurant_list[i]] = est_rating
            if (est_rating > avg_rating):
                rec_list.append(restaurant_list[i])

        
        #rating_dict = {k: v for k, v in sorted(rating_dict.items(), key=lambda item: item[0])}
        #res = dict(sorted(rating_dict.items(), key = itemgetter(1), reverse = True)[:topN])
        
        #return list(res.keys())
        return rec_list
    
    
    else:
        print('use profile')
        profile_np = profile_df.to_numpy()
        item=[]
        user=[]
        rating=[]
        profile={}
        profile2={}
        
        dict_kid = {}
        dict_relationship = {}
        dict_veg = {}
        dict_religion = {}
        
        dict_kid['no'] = 0
        dict_kid['yes'] = 1
        dict_relationship['no'] = 0
        dict_relationship['yes'] = 1
        dict_veg['vegetarian'] = 0
        dict_veg['vegan'] = 1
        dict_veg['none'] = 2
        dict_religion['halal'] = 0
        dict_religion['kosher'] = 1
        dict_religion['none'] = 2
        
        loc_age = profile_df.columns.get_loc("age")
        loc_kids = profile_df.columns.get_loc("kids")
        loc_relation = profile_df.columns.get_loc("relationship")
        loc_veg = profile_df.columns.get_loc("veg")
        loc_rel = profile_df.columns.get_loc("religion")
        loc_user = profile_df.columns.get_loc("_id")

        for k in range(len(profile_np)):
            profile[str(profile_np[k][loc_user])] = [profile_np[k][loc_age], dict_kid[profile_np[k][loc_kids]], dict_relationship[profile_np[k][loc_relation]], dict_veg[profile_np[k][loc_veg]],dict_religion[profile_np[k][loc_rel]]]
    
        user_id = userId
        user_profile = profile[user_id]
        correlation = {}
        
        for key in profile:
            corr = stats.pearsonr(user_profile, profile[key])[0]
            correlation[key] = corr

        top_x = min(userCountCut+1, len(profile_np))
        sorted_top_correlation = dict(sorted(correlation.items(), key=operator.itemgetter(1), reverse=True)[:top_x])
        
        recom_list = []
        
        loc_res = reviews_df.columns.get_loc("restaurantId")

        
        for key in sorted_top_correlation:
            review_list_1 = reviews_df[reviews_df['userId']==key]
            review_list = review_list_1[review_list_1['review']==str(3)]
            
            #print(review_list)
            review_list_np = review_list.to_numpy()
            for i in range(len(review_list_np)):
                if review_list_np[i][loc_res] in restaurant_list: 
                    recom_list = recom_list + [review_list_np[i][loc_res]]
        
        print(recom_list)
        
        return recom_list
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    