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
    top_n = int(request.args.get("top_n", None))

    list = recommend.recommend(user_id, rest_list, review_cut, top_n)
    return jsonify(list)


if __name__ == '__main__':
    app.run(threaded=True, port=6000, debug=True, use_reloader=True)
    




        

