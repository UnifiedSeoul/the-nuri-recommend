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
        if recommend_jobId:
            # api 요청
            url = 'http://127.0.0.1:5000/api/recommend/result'
            json_data = {"recommendJobId": recommend_jobId}
            post_response = requests.post(url, json=json_data)
            if post_response.status_code == 200:
                return post_response.text, 200
            else:
                print("POST 요청에 실패했습니다. 상태 코드:", post_response.status_code)
        
        return ' ', post_response.status_code

@app.route('/api/recommend/result', methods=['POST'])
def check_recommend():
    request_data = request.get_json()
    return request_data


if __name__ == '__main__':
    app.run(debug=True)
