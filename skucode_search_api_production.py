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

###given sku get product details
def sku_details_fetch(sku_code):
    hed = {'Authorization': 'bearer '+ auth_token , 'Content-Type':'application/json'}
    data1 = '''{"code":'''+"'"+str(sku_code)+"'"+'''}'''
    url = 'https://epprod.tqdigital-cf-ep.net/cortex/lookups/cf/items/form?followlocation'
    response_search = requests.post(url,data=data1 ,headers=hed)   
    sku_prod_url = str(response_search.json()['self']['href'])
    hed1 = {'Authorization': 'bearer '+ auth_token , 'Content-Type':'application/json'}
    url1 = sku_prod_url + '?zoom=definition,definition:options:element,definition:options:element:value'
    sku_search = requests.get(url1,headers=hed1)
    display_name = str(sku_search.json()['_definition'][0]['display-name'])
    names = []
    values = []
    for i in sku_search.json()['_definition'][0]['_options'][0]['_element']:
        names.append(str(i['display-name']))
        values.append(str(i['_value'][0]['display-name']))
    image_url = product_image(sku_code)
    val = {}
    val['product_name'] = display_name
    val['product_attributes'] = values
    val['product_attribute_names'] = names
    val['product_image'] = image_url
    val['sku_code'] = sku_code
    hed2 = {'Authorization': 'bearer '+ auth_token , 'Content-Type':'application/json'}
    url2 = sku_prod_url + '?zoom=definition:fromprice'
    sku_price_search = requests.get(url2,headers=hed2)
    val['price'] = str(sku_price_search.json()['_definition'][0]['_fromprice'][0]['from-price'][0]['display'])
    return val

## Master code to fetch the data
def master_sku_data_fetch(code):
    cnx = mysql.connector.connect(user='dhiranj', password='dhir@nj123',
                              host='34.227.26.122', port = 3306,
                              database='COMMERCEDB')
    df = pd.read_sql('SELECT * FROM COMMERCEDB.TPRODUCTSKU WHERE SKUCODE = '+'"'+str(code)+'"', con=cnx)
    # df = pd.read_sql('SELECT distinct UIDPK FROM COMMERCEDB.TPRODUCTSKU', con=cnx)
    product_uid = df['PRODUCT_UID'][0]
    df1 = pd.read_sql('SELECT * FROM COMMERCEDB.TPRODUCTSKU WHERE PRODUCT_UID = '+str(product_uid), con=cnx)
    sku_codes = list(df1['SKUCODE'])
    master_data = []
    for i,elem in enumerate(sku_codes):
        if i < 4:
            try:
                master_data.append(sku_details_fetch(elem))
            except:
                pass
    return master_data

@app.route('/', methods=['GET'])
@cross_origin(supports_credentials=True)
def home():
    return '''<h1>SKUCODE search api</h1>
<p>API that takes SKU codes as input and gives the relevant product details as output.</p>'''


@app.route('/Dialogflow/getProductSuggestions', methods=['GET'])
@cross_origin(supports_credentials=True)
def api_all():
	query_parameters = request.args
	sku_code = query_parameters.get('sku_code')
	newval = master_sku_data_fetch(str(sku_code).replace('%20',' '))
	return jsonify(newval)
#app.run()
app.run(host = "192.168.2.193", port = 5012)
