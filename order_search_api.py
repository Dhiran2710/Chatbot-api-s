import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
import sqlite3
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import pickle
import operator
import csv
import os
import requests
import pprint
import ast
import json
import mysql.connector
import datetime

app = flask.Flask(__name__)
CORS(app, support_credentials=True)
app.config["DEBUG"] = True

##Call to generate product image url
def product_image(code):
    url = 'https://s3-us-west-2.amazonaws.com/commercefactory/Images/'+code+'/'+code+'.jpg'
    return url
    

@app.route('/', methods=['GET'])
@cross_origin(supports_credentials=True)
def home():
    return '''<h1>Order id search api</h1>
<p>API that takes order id as input and gives the order details as output.</p>'''


@app.route('/Dialogflow/getSuggestions', methods=['GET'])
@cross_origin(supports_credentials=True)
def api_all():
	query_parameters = request.args
	order_id = str(query_parameters.get('order_id'))
	cnx = mysql.connector.connect(user='dhiranj', password='dhir@nj123',
                              host='34.227.26.122', port = 3306,
                              database='COMMERCEDB')
	try:
		df = pd.read_sql('SELECT * FROM COMMERCEDB.TORDERSKU WHERE UIDPK = '+order_id, con=cnx)
		retrun_val = {}
		retrun_val['order_id'] = str(df['UIDPK'][0])
		retrun_val['sku_code'] = str(df['SKUCODE'][0])
		retrun_val['image'] = product_image(str(df['SKUCODE'][0]))
		retrun_val['order_time'] = str(df['CREATED_DATE'][0])
		retrun_val['name'] = str(df['DISPLAY_NAME'][0])
	except:
		retrun_val = ['OrderId is not available']
		pass
	newval = retrun_val
	return jsonify(newval)
app.run(host = "192.168.2.193", port = 5010)

#app.run(host = "192.168.2.193", port = 5010,ssl_context='adhoc')

#http://192.168.2.193:5010/Dialogflow/getSuggestions?order_id=20011