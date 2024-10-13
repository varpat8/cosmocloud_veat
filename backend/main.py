from flask import Flask, jsonify, request
import requests
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


swiggy_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def process_external_swiggy_search(lat, long, query):
    SWIGGY_SEARCH_URL = f"https://www.swiggy.com/dapi/restaurants/search/v3?lat={lat}&lng={long}&str={query}&submitAction=ENTER"
    response = requests.get(SWIGGY_SEARCH_URL, headers=swiggy_headers)
    if response.status_code != 200:
        return []
    response = response.json()
    data = response['data']
    cards = data['cards']
    # if len(cards) < 2:
    #     return []
    # grouped_cards = cards[1]["groupedCard"]["cardGroupMap"]["RESTAURANT"]["cards"]
    restaurants = []
    for card_in_data in cards:
        if "groupedCard" not in card_in_data: continue
        grouped_cards = card_in_data["groupedCard"]["cardGroupMap"]["RESTAURANT"]["cards"]
        for _, grouped_card_info in enumerate(grouped_cards):
            card_in_grouped_cards = grouped_card_info["card"]["card"]
            card_type = card_in_grouped_cards["@type"]
            if card_type == "type.googleapis.com/swiggy.presentation.food.v2.Restaurant":
                info = card_in_grouped_cards["info"]
                restaurants.append(info["slugs"]["restaurant"])
            elif card_type == "type.googleapis.com/swiggy.presentation.food.v2.RestaurantCollection":
                restaurants_collection = card_in_grouped_cards["restaurants"]
                for _, restaurant_in_collection in enumerate(restaurants_collection):
                    info = restaurant_in_collection["info"]
                    restaurants.append(info["slugs"]["restaurant"])
    return restaurants


def process_external_swiggy_restaurant_menu(lat, long, restaurant_id):
    SWIGGY_MENU_URL = f"https://www.swiggy.com/dapi/menu/pl?page-type=REGULAR_MENU&complete-menu=true&lat={lat}&lng={long}&restaurantId={restaurant_id}&catalog_qa=undefined&submitAction=ENTER"
    response = requests.get(SWIGGY_MENU_URL, headers=swiggy_headers)
    if response.status_code != 200:
        return []
    response = response.json()
    data = response['data']
    cards = data['cards']
    menu_items = []
    for card_in_data in cards:
        if "groupedCard" not in card_in_data: continue
        grouped_cards = card_in_data["groupedCard"]["cardGroupMap"]["REGULAR"]["cards"]
        for _, grouped_card_info in enumerate(grouped_cards):
            card_in_grouped_cards = grouped_card_info["card"]["card"]
            card_type = card_in_grouped_cards["@type"]
            if card_type == "type.googleapis.com/swiggy.presentation.food.v2.ItemCategory":
                item_cards = card_in_grouped_cards["itemCards"]
                for item_card in item_cards:
                    inner_card = item_card["card"]
                    if inner_card["@type"] == 'type.googleapis.com/swiggy.presentation.food.v2.Dish':
                        menu_items.append(inner_card["info"]["name"])
    return menu_items


@app.route('/swiggy-menu-items', methods=['GET'])
def swiggy_menu_items():
    # lat = request.args.get('lat')
    # long = request.args.get('long')
    # query = request.args.get('query')
    lat = 12.984048
    long = 77.7481552
    restaurant_id = 345899
    menu_items = process_external_swiggy_restaurant_menu(lat, long, restaurant_id)
    return menu_items


@app.route('/swiggy-search', methods=['GET'])
def swiggy_search():
    # lat = request.args.get('lat')
    # long = request.args.get('long')
    # query = request.args.get('query')
    lat = 12.984048
    long = 77.7481552
    query = "paradise"
    suggested_restaurants = process_external_swiggy_search(lat, long, query)
    return suggested_restaurants


def process_external_zomato_location(lat, long):
    ZOMATO_LOCATION_URL = f"https://www.zomato.com/webroutes/location/get?lat={lat}&lon={long}&entity_id=0&entity_type=&userDefinedLatitude=0&userDefinedLongitude=0&placeId=0&placeType=&placeName=&cellId=0&addressId=0&isOrderLocation=0&forceEntityName=&res_id=0&pageType=city&persist=true"
    response = requests.get(ZOMATO_LOCATION_URL, headers=swiggy_headers)
    if response.status_code != 200:
        return []
    return response.json()["locationDetails"]


def process_external_zomato_search(params):
    ZOMATO_SEARCH_URL = f"https://www.zomato.com/webroutes/search/autoSuggest"
    response = requests.get(ZOMATO_SEARCH_URL, headers=swiggy_headers, params=params)
    if response.status_code != 200:
        return []
    response = response.json()
    if 'results' not in response:
        return []
    restaurants = []
    results = response['results']
    for entity in results:
        if entity['entityType'] == "restaurant":
            restaurants.append(entity["info"]["name"])
    return restaurants


@app.route('/zomato-search', methods=['POST'])
def zomato_search():
    data = request.json
    query = data.get("query")
    lat = data.get("lat")
    long = data.get("long")
    params = process_external_zomato_location(lat, long)
    params["q"] = query
    suggested_restaurants = process_external_zomato_search(params)
    # print(suggested_restaurants)
    return suggested_restaurants


@app.route('/zomato-menu', methods=['GET'])
def get_zomato_menu():
    auth_token = get_zomato_auth_token()

    headers = {
        'Authorization': f'Bearer {auth_token}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    try:
        response = requests.get(
            'https://www.zomato.com/webroutes/getPage?page_url=/hyderabad/paradise-biryani-a-legend-since-1953-gachibowli/order&location=&isMobile=0',
            headers=headers
        )

        if response.status_code == 200:

            data = response.json()

            menus = data['page_data']['order']['menuList']['menus']

            all_items = []

            for menu_data in menus:
                categories = menu_data['menu']['categories']
                for category_data in categories:
                    items = category_data['category']['items']
                    for item_data in items:

                        item_info = {
                            "name": item_data['item']['name'],
                            "price": item_data['item']['price'],
                            "image_url": item_data['item'].get('item_image_thumb_url', None), 
                            "rating": item_data['item'].get('rating', None) 
                        }
                    
                        all_items.append(item_info)

            return jsonify({"items": all_items}), 200

        else:
            return jsonify({"error": "Failed to fetch data from Zomato"}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500



def get_zomato_auth_token():
    try:
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
        response = requests.get('https://www.zomato.com/webroutes/auth/csrf', headers=headers)
        if response.status_code == 200:
            data = response.json()
            csrf_token = data.get('csrf', None)
            if csrf_token:
                return csrf_token
            else:
                raise Exception("CSRF token not found in the response.")
        else:
            raise Exception("Failed to get CSRF token.")
    except Exception as e:
        raise Exception(f"Error fetching auth token: {str(e)}")
    

if __name__ == '__main__':
    app.run(debug=True)
