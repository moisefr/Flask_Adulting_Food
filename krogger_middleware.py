import asyncio
import json
import geocoder
import requests
from base64 import b64encode

#Get Config Values
def load_config(fname='./Kroger-Production_environment.json'):
    config = None
    with open(fname) as f:
        config = json.load(f)
    return config
configuration_var = load_config()

def get_zip_code():
    g = geocoder.ip('me')
    zip_code = g.postal
    return zip_code
def authorize():
        base_url = "https://api.kroger.com/v1/connect/oauth2/token?grant_type=client_credentials"
        payload={'scope': 'product.compact'}
        client_id = configuration_var["web"]["kroger-clientId"]
        client_secret = configuration_var["web"]["kroger-clientSecret"]
        data = bytes(client_id + ":"+ client_secret, 'utf-8')
        encoded_string = b64encode(data)
        huh = str(encoded_string)
        final_encode = huh[huh.find("b'")+2:huh.find("=")+1]
        response = requests.request("POST", base_url, data = payload, headers = {'Authorization': 'Basic {}'.format(final_encode), 'Content-Type': 'application/x-www-form-urlencoded'})
        access_token = response.text[response.text.find('access_token":')+len('access_token')+3:response.text.find("token_type")-3]
        # print("#access TOKEN - 🟢: \n" + access_token)
        return access_token

def store_locator(zipcode, access_token):
        url = "https://api.kroger.com/v1/locations?filter.zipCode.near={zip_code}&filter.radiusInMiles=60".format(zip_code=zipcode)
        headers = {'Authorization': 'Bearer {token}'.format(token = access_token)}
        response = requests.request("GET", url, headers=headers)
        holder = response.json()
        locationids = []
        for item in holder['data']:
            for key in item.keys():
                if key == "hours":
                    locationids.append(item['locationId'])
        locationids = list(set(locationids))
        return locationids

def product_price(product, access_token, locationid):
    url = "https://api.kroger.com/v1/products?filter.term={product_name}&filter.locationId={location_id}&filter.limit=1".format(product_name = product, location_id = locationid)
    headers = {'Authorization': 'Bearer {token}'.format(token = access_token)}
    response = requests.request("GET", url, headers=headers)
    print(response.text)
    return

class Engine():
    ItemBag = []
    def product_price(product):
        return "you thought like shit"

