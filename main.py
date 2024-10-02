from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/swiggy-search', methods=['GET'])
def swiggy_search():
    lat = request.args.get('lat')
    long = request.args.get('long')
    query = request.args.get('query')
    # response = requests.get('https://www.zomato.com/webroutes/getPage?page_url=/hyderabad/paradise-biryani-a-legend-since-1953-gachibowli/order&location=&isMobile=0',
    return "items", 200


if __name__ == '__main__':
    app.run(debug=True)
