# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import recommend

from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/')
def hello():
    return "hello"


@app.route('/recommend')
def rec():
    user_id = str(request.args.get("user_id", None))
    rest_list = request.args.get("rest_list", None)
    review_cut = int(request.args.get("review_cut", None))
    user_cut = int(request.args.get("user_cut", None))

    list = recommend.recommend(user_id, rest_list, review_cut, user_cut)
    return jsonify(list)


if __name__ == '__main__':
    app.run(threaded=True, port=8000, debug=True, use_reloader=True)
    




        

