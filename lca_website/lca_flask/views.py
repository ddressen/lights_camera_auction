from flask import request
from flask import render_template
from lca_flask import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2

from ebay_model_3 import URLFromID, ImageFMBlur, Symmetry, PriceModel, ListingTitle, CurrentPrice, PhotoNum, PhotoInc, PriceInc, PriceRange

user = 'donalddressen' #add your username here (same as previous postgreSQL)            
host = 'localhost'
dbname = 'birth_db'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

@app.route('/')  
@app.route('/index')
def index():
    '''Organize the home page with the Jumbotron template'''

    return render_template("jumbotron.html")

@app.route('/about_me')
def aboutme():
    '''Return info about me'''

    return render_template("aboutme.html")

@app.route('/algorithm')
def algorithm():
    '''Information about how it works'''

    return render_template("algorithm.html")

@app.route('/validation')
def validation():
    '''Plots and tables showing validation, with text in between'''

    return render_template("validation.html")

# Add "Input" and make it the home page too
@app.route('/input')
def itemID_input():
    return render_template("input.html")

@app.route('/output')
def itemID_output():
    item_ID = request.args.get('item_ID')
    listing_title = ListingTitle(item_ID)
    current_price = CurrentPrice(item_ID)
    est_price = PriceModel(item_ID)
    photo_num = PhotoNum(item_ID)
    photo_inc = PhotoInc(item_ID)
    price_inc = PriceInc(item_ID)
    url = URLFromID(item_ID)
    
    est_price_2 = est_price + price_inc
    price_range_low, price_range_hi = PriceRange(item_ID)
    
    blur_list = ImageFMBlur(item_ID)
    blur = blur_list[1]
    
    if blur == 1:
        blurry = 'Yes'
    else:
        blurry = 'No'
    
    symm_list = Symmetry(item_ID)
    symm = symm_list[0]
    
    if symm < 50000:
        too_symm = 'Yes'
    else:
        too_symm = 'No'
        
    if price_range_low < current_price:
        price_range_low = current_price
        
    return render_template("output.html", 
                           listing_title = listing_title, 
                           est_price = est_price, 
                           photo_num = photo_num,
                           current_price = current_price,
                           photo_inc = photo_inc,
                           est_price_2 = est_price_2,
                           price_range_low = price_range_low,
                           price_range_hi = price_range_hi,
                           blurry = blurry,
                           too_symm = too_symm,
                           url = url
                          )