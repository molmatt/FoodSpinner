from flask import render_template, Flask, request
import googlemaps as gmaps
import pandas as pd
import os

# Localizing config variable
gmAPI = os.environ.get('gmapsAPI')

# Initialize app
app = Flask(__name__, static_url_path='/static')

# Starting page with form
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

# Restaurant suggestion page
@app.route('/results', methods=['GET', 'POST'])
def results():
    specs = request.form.to_dict()
    result = FoodSpinner(address = specs['address'],
                style = specs['style'],
                price = int(specs['price']),
                rating = float(specs['rating']),
                distance = specs['distance'],
                choices = int(specs['choices']))
    return render_template('results.html', nam=result['Name'], rat=result['Rating'], ratc=result['Rating Count'], pri=result['Price'])



def FoodSpinner(address, style=None, price = 2, rating = 4, distance=1000, choices=1, nowOpen=True):
    gmapi = gmaps.Client(key=gmAPI)
    addy = gmapi.geocode(address)
    latlon = addy[0]['geometry']['location']
    srch = gmapi.places_nearby(location=latlon, radius=distance, type='restaurant', keyword=style)
    names = []
    prices = []
    ratings = []
    numRatings = []
    for i in srch['results']:
        names.append(i['name'])
        prices.append(i['price_level']) if 'price_level' in i.keys() else prices.append(np.nan)
        ratings.append(i['rating'])
        numRatings.append(i['user_ratings_total'])
    df = pd.DataFrame({
        'Name' : names,
        'Price' : prices,
        'Rating' : ratings,
        'Rating Count' : numRatings
    })
    print(len(df.index), 'matching this cuisine in range')
    df.drop(df.index[df['Price'] > price], inplace=True)
    print(len(df.index), 'meeting the price cutoff')
    df.drop(df.index[df['Rating'] < rating], inplace=True)
    print(len(df.index), 'meeting the rating cutoff')
    return(df.sample(choices).reset_index().iloc[:,1:])
