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

###Function to get all the product ulr's wrt search and also get the details
def prod_master_details(product):
    hed = {'Authorization': 'bearer '+ auth_token , 'Content-Type':'application/json'}
    data1 = '''{"keywords":'''+"'"+str(product)+"'"+'''}'''
    url = 'https://epprod.tqdigital-cf-ep.net/cortex/searches/cf/keywords/form/?followlocation'
    response_search = requests.post(url,data=data1 ,headers=hed)

    product_links = []
    for i in response_search.json()['links']:
        product_links.append(i['href'])
    product_details = []
    for i in product_links:
        try:
            product_details.append(get_product_details(i))
        except:
            pass
    return product_details


@app.route('/', methods=['GET'])
@cross_origin(supports_credentials=True)
def home():
    return '''<h1>Product search api</h1>
<p>API that takes search keywords as input and gives the relevant product details as output.</p>'''


@app.route('/Dialogflow/getProductSuggestions', methods=['GET'])
@cross_origin(supports_credentials=True)
def api_all():
	query_parameters = request.args
	product_search_query = query_parameters.get('product_search_query')
	newval = prod_master_details(str(product_search_query).replace('%20',' '))
	return jsonify(newval)
#app.run()
app.run(host = "192.168.2.193", port = 5011)

#http://192.168.2.193:5011/Dialogflow/getProductSuggestions?product_search_query=apple