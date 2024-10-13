from flask import Flask, jsonify
from flask_cors import CORS
import requests



app = Flask(__name__)
CORS(app)


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