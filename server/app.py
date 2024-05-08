import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from flask import Flask, request, jsonify
from recommend.RecommendJob import *

app = Flask(__name__)

@app.route('/api/recommend', methods=['POST'])
def get_user_data():
    if request.method == 'POST':
        request_data = request.get_json()
        recommend_jobId = recommendation(request_data)
        print("send ", recommend_jobId)
        if recommend_jobId:
            return {"recommendJobId": recommend_jobId}, 200
        else:
            return 400

@app.route('/api/recommend/result', methods=['POST'])
def check_recommend():
    request_data = request.get_json()
    return request_data


if __name__ == '__main__':
    app.run(debug=True)
