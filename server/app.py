import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from waitress import serve
from flask import Flask, request, jsonify, abort
from recommend.RecommendJob import *
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://43.200.89.34"}})

def setup_logging():
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

@app.route('/api/recommend', methods=['POST'])
def get_user_data():
    if request.method == 'POST':
        print(request)
        request_data = request.get_json()
        recommend_jobId = recommendation(request_data)
        print("send ", recommend_jobId)
        if recommend_jobId:
            return {"recommendJobId": recommend_jobId}, 200
        else:
            abort(400)

@app.route('/api/recommend/result', methods=['POST'])
def check_recommend():
    request_data = request.get_json()
    return request_data


if __name__ == '__main__':
    setup_logging()
    serve(app, host='0.0.0.0', port=5000)
