import datetime
import mysql.connector
import pandas as pd
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

###Token generator
def response_token_generator():
    hed = {'Content-Type': 'application/x-www-form-urlencoded'}
    url = 'https://epprod.tqdigital-cf-ep.net/cortex/oauth2/tokens/?grant_type=password&role=REGISTERED&scope=cf&username=dhiranjamana1027@gmail.com&password=Dhiran@123'
    response_key_token = requests.post(url, headers=hed)
    return str(response_key_token.json()['access_token'])
auth_token = response_token_generator()

###Function to get details of each product when an url is given
def get_product_details(url):
    hed = {'Authorization': 'bearer '+ auth_token , 'Content-Type':'application/json'}
    url = url + '?zoom=code,definition:options:element:value,price,definition'
    response_search = requests.get(url,headers=hed)
    val = {}
    val['sku_code'] = str(response_search.json()['_code'][0]['code'])
    product_values = []
    for i in response_search.json()['_definition'][0]['_options'][0]['_element']:
        product_values.append(str(i['_value'][0]['display-name']))
    val['product_attributes'] = product_values
    val['price'] = str(response_search.json()['_price'][0]['purchase-price'][0]['amount'])
    val['product_name'] = str(response_search.json()['_definition'][0]['display-name'])
    val['product_image'] = product_image(str(response_search.json()['_code'][0]['code']))
    return val

##Code to get all the cross sell products wrt sku code	
def cross_details(sku_code):
    sku_code = sku_code
    hed = {'Authorization': 'bearer '+ auth_token , 'Content-Type':'application/json'}
    data1 = '''{"code":'''+"'"+str(sku_code)+"'"+'''}'''
    url = 'https://epprod.tqdigital-cf-ep.net/cortex/lookups/cf/items/form?followlocation'
    response_search = requests.post(url,data=data1 ,headers=hed)      
    for i in response_search.json()['links']:
        if i["rel"] == 'recommendations':
            cross_sell_url = str(i["href"])   
    hed1 = {'Authorization': 'bearer '+ auth_token , 'Content-Type':'application/json'}
    url1 = cross_sell_url + '?zoom=crosssell'
    sku_search = requests.get(url1,headers=hed1)   
    product_links = []
    for i in sku_search.json()['_crosssell'][0]['links']:
        if str(i['rel']) != 'next':
            product_links.append(i['href'])  
    master_data = []
    for i,elem in enumerate(product_links):
            try:
                master_data.append(get_product_details(elem))
            except:
                pass        
    return master_data

@app.route('/', methods=['GET'])
@cross_origin(supports_credentials=True)
def home():
    return '''<h1>CROSS-SELL search api</h1>
<p>API that takes SKU codes as input and gives the cross-sell product details as output.</p>'''


@app.route('/Dialogflow/getCrossSellSuggestions', methods=['GET'])
@cross_origin(supports_credentials=True)
def api_all():
	query_parameters = request.args
	sku_code = query_parameters.get('sku_code')
	newval = cross_details(str(sku_code).replace('%20',' '))
	return jsonify(newval)
#app.run()
app.run(host = "0.0.0.0", port = 5010,ssl_context=('cert.crt', 'key.key'), threaded=True, debug=True)
