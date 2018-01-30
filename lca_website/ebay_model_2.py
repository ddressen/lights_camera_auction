import pandas as pd
import pickle

import ebaysdk
from ebaysdk.finding import Connection as Finding
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError

def ItemCall(item_ID):
    api = Trading(config_file='ebay2.yaml')
    response = api.execute('GetItem', {
            'itemID': item_ID,
            'IncludeItemSpecifics': True,
            'DetailLevel':'ItemReturnDescription'
        })
    dictstr = response.dict()
    return dictstr

def ListingTitle(item_ID):
    dictstr = ItemCall(item_ID)
    listing_title = dictstr['Item']['Title']
    return listing_title

def CurrentPrice(item_ID):
    dictstr = ItemCall(item_ID)
    current_price = int(float(dictstr['Item']['SellingStatus']['CurrentPrice']['value']))
    return current_price

def PhotoNum(item_ID):
    dictstr = ItemCall(item_ID)
    if type(dictstr['Item']['PictureDetails']['PictureURL']) == list:
        photo_num = len(dictstr['Item']['PictureDetails']['PictureURL'])
    else:
        photo_num = 1
    return photo_num

def PhotoInc(item_ID):
    photo_num = PhotoNum(item_ID)
    photo_inc = (24-photo_num)
    return photo_inc

def PriceInc(item_ID):
    photo_inc = PhotoInc(item_ID)
    price_inc = 231*photo_inc
    return price_inc

def PriceRange(item_ID):
    est_price = PriceModel(item_ID)
    price_range_low = est_price - 1200
    price_range_hi = est_price + 1200
    return (price_range_low, price_range_hi)

def PriceModel(item_ID):
    dictstr = ItemCall(item_ID)
    
    category_ids = []
    condition_ids = []
    item_ids = []
    payment_methods = []
    seller_percents = []
    seller_scores = []
    seller_stars = []
    top_rateds = []
    reserves = []
    start_prices = []
    photo_nums = []
    postal_codes = []
    years = []
    mileages = []
    
    category_ids.append(dictstr['Item']['PrimaryCategory']['CategoryID'])
    condition_ids.append(dictstr['Item']['ConditionID'])
    item_ids.append(dictstr['Item']['ItemID']) 
    payment_methods.append(len(dictstr['Item']['PaymentMethods']))
    seller_percents.append(float(dictstr['Item']['Seller']['PositiveFeedbackPercent']))
    seller_scores.append(int(dictstr['Item']['Seller']['FeedbackScore']))
    seller_stars.append(dictstr['Item']['Seller']['FeedbackRatingStar'])
    
    try:
        top_rateds.append(dictstr['Item']['Seller']['SellerInfo']['TopRatedSeller']) #Problem: No top rated info; assume to be 0?
    except:
        top_rateds.append('False')
        
    reserves.append(dictstr['Item']['ListingDetails']['HasReservePrice'])
    start_prices.append(float(dictstr['Item']['StartPrice']['value']))
    
    try:
        postal_codes.append(int(dictstr['Item']['PostalCode']))
    except:
        postal_codes.append(0)
    
    try:
        if type(dictstr['Item']['PictureDetails']['PictureURL']) == list:
            photo_nums.append(len(dictstr['Item']['PictureDetails']['PictureURL']))
        else:
            photo_nums.append(1)
    except:
        photo_nums.append(0)
        
    try:
        for item in dictstr['Item']['ItemSpecifics']['NameValueList']:        
            if 'Mileage' in list(item.values()):
                mileages.append(int(list(item.values())[1]))
        
        if len(mileages) < 1:
            mileages.append(-1)
            
    except:
        mileages.append(-1)
    
    try:
        for item in dictstr['Item']['ItemSpecifics']['NameValueList']:
            if 'Year' in list(item.values()):
                years.append(int(list(item.values())[1]))
    
        if len(years) < 1:
            years.append(0)
    
    except:
        years.append(0)
    
    
    listing_df = pd.DataFrame(
    {'category ID': category_ids,
     'condition ID': condition_ids,
     'item ID': item_ids,
     'number of payment methods': payment_methods,
     'seller percent': seller_percents,
     'seller score': seller_scores,
     'seller star': seller_stars,
     'top rated': top_rateds,
     'reserve': reserves,
     'start price': start_prices,
     'photo number': photo_nums,
     'postal code': postal_codes,
     'year': years,
     'mileage': mileages
    })
    
    star_mapping = {"None": 0, 
                "Yellow": 1, 
                "Blue": 2, 
                "Turquoise": 3, 
                "Purple": 4,
                "Red": 5,
                "Green": 6,
                "YellowShooting": 7,
                "TurquoiseShooting": 8,
                "PurpleShooting": 9,
                "RedShooting": 10,
                "GreenShooting": 11,
                "SilverShooting": 12
               }

    listing_df['seller star'] = listing_df['seller star'].map(star_mapping)
    listing_df['seller star'] = listing_df['seller star'].fillna(0)
    
    listing_df['top rated'] = listing_df['top rated'].replace('False', 0)
    listing_df['top rated'] = listing_df['top rated'].replace('false', 0)
    listing_df['top rated'] = listing_df['top rated'].replace('True', 1)
    listing_df['top rated'] = listing_df['top rated'].replace('true', 1)
    
    listing_df['reserve'] = listing_df['reserve'].replace('false', 0)
    listing_df['reserve'] = listing_df['reserve'].replace('true', 1)
    
    listing_df = listing_df[['category ID', 
                         'condition ID', 
                         'item ID', 
                         'number of payment methods', 
                         'seller percent', 
                         'seller score',
                         'seller star',
                         'top rated',
                         'reserve',
                         'start price',
                         'photo number',
                         'postal code',
                         'year',
                         'mileage'
                        ]]
    
    # load the model from disk and estimate the selling price
    loaded_model = pickle.load(open('finalized_model_2.sav', 'rb'))
    est_price = loaded_model.predict(listing_df)
    est_price = int(est_price)
    return est_price