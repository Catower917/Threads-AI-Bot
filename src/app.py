import os
import threading
import requests
from flask import Flask, request, redirect, jsonify
from src import bot  # src 디렉토리의 bot.py를 임포트

app = Flask(__name__)

# 환경 변수에서 클라이언트 정보 로드
CLIENT_ID = os.getenv("APP_ID")
CLIENT_SECRET = os.getenv("APP_SECRET")
REDIRECT_URI = "https://oaao.onrender.com/callback"
SCOPE = "threads_basic"
AUTH_URL = "https://threads.net/oauth/authorize"
TOKEN_URL = "https://graph.threads.net/oauth/access_token"
LONG_LIVED_TOKEN_URL = "https://graph.threads.net/access_token"
RESPONSE_TYPE = "code"

@app.route('/')
def home():
    return "AI Bot Server Running!"

@app.route('/login')
def login():
    auth_redirect_url = (
        f"{AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}&response_type={RESPONSE_TYPE}"
    )
    return redirect(auth_redirect_url)

@app.route('/callback')
def callback():
    code = request.args.get("code")
    if not code:
        return "Error: No code received", 400

    # 짧은 액세스 토큰 요청
    token_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(TOKEN_URL, data=token_data)
    
    if response.status_code == 200:
        token_info = response.json()
        short_lived_access_token = token_info.get('access_token')
        
        # 짧은 토큰을 장기 토큰으로 교환
        long_token_data = {
            'grant_type': 'th_exchange_token',
            'client_secret': CLIENT_SECRET,
            'access_token': short_lived_access_token
        }
        long_token_response = requests.get(LONG_LIVED_TOKEN_URL, params=long_token_data)
        
        if long_token_response.status_code == 200:
            long_token_info = long_token_response.json()
            long_lived_access_token = long_token_info.get('access_token')
            expires_in = long_token_info.get('expires_in')

            # 토큰 저장 (실제 환경에서는 안전한 저장 방법 고려)
            os.environ["ACCESS_TOKEN"] = long_lived_access_token
            
            return jsonify({
                "message": "Long-lived access token received!",
                "long_lived_access_token": long_lived_access_token,
                "expires_in": expires_in
            })
        else:
            return jsonify({"error": "Failed to exchange for long-lived token", "details": long_token_response.json()}), 400
    else:
        return jsonify({"error": "Failed to get access token", "details": response.json()}), 400

# 외부 스케줄러 (예: cron-job.org)에서 호출할 엔드포인트
@app.route('/runbot', methods=['GET'])
def run_bot():
    thread = threading.Thread(target=bot.main)
    thread.start()
    return jsonify({"message": "Bot execution started!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
