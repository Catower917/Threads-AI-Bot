import os
import openai
import requests
from dotenv import load_dotenv
from src.prompt import get_prompt
from langchain_community.tools.tavily_search import TavilySearchResults

# .env 파일 로드
load_dotenv()

# 환경 변수에서 액세스 토큰 및 API 키 로드
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # TAVILY API 키
USER_ID = os.getenv("USER_ID")  # Threads 사용자 ID

# OpenAI API 설정
openai.api_key = OPENAI_API_KEY
BASE_URL = "https://graph.threads.net/v1.0"

def upload_post(access_token: str, text: str):
    """
    Threads API를 사용하여 게시물을 업로드합니다.
    """
    if not access_token or not text:
        return {"error": "Missing access token or text for post"}

    # Step 1: 텍스트 게시물 생성
    media_url = f"{BASE_URL}/{USER_ID}/threads"
    payload = {
        'media_type': 'TEXT',
        'text': text,
        'access_token': access_token
    }
    response = requests.post(media_url, data=payload)
    container_id = response.json().get('id')
    if not container_id:
        return {"error": "Failed to create media container", "details": response.json()}

    # Step 2: 게시물 게시
    publish_url = f"{BASE_URL}/{USER_ID}/threads_publish"
    payload = {
        'creation_id': container_id,
        'access_token': access_token
    }
    publish_response = requests.post(publish_url, data=payload)
    if publish_response.status_code == 200:
        return {
            "message": "[+] 게시물 업로드 완료",
            "container_id": container_id
        }
    else:
        return {
            "error": "Failed to publish post",
            "details": publish_response.json()
        }

def generate_thread_post(prompt):
    """
    OpenAI API를 사용하여 게시물 콘텐츠를 생성합니다.
    """
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "너는 Meta Threads에서 활동하는 PurpleAILAB의 대표이자 AI Agent에 관심있는 SNS 콘텐츠 제작 전문가, 민P야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        text = response.choices[0].message.content.strip()
        print("게시물 내용:")
        print(text)
        return text

    except openai.OpenAIError as e:
        print(f"OpenAI API 오류 발생: {e}")
        return {"error": f"OpenAI API 오류 발생: {e}"}
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")
        return {"error": f"알 수 없는 오류 발생: {e}"}

def search_web(topic: str) -> str:
    """
    TAVILY Search API를 사용하여 주제에 관한 최신 정보를 검색합니다.
    """
    search_tool = TavilySearchResults(max_results=3)
    search_results = search_tool.invoke(topic)
    
    result_texts = []
    for result in search_results:
        url = result.get("url", "")
        content = result.get("content", "")
        result_texts.append(f"URL: {url}\nContent: {content}")
    return "\n\n".join(result_texts)

import json

def main():
    topics = ["AI"]
    
    for topic in topics:
        news = search_web(topic)
        prompt = get_prompt(topic, news)
    
        if ACCESS_TOKEN:
            text = generate_thread_post(prompt)
            
            # 게시물 내용이 500자를 초과할 경우 재생성 (최대 3회)
            max_retry = 3
            retry_count = 0
            upload_result = upload_post(ACCESS_TOKEN, text)
            while (
                "error" in upload_result and
                "Param text must be at most 500 characters long." in upload_result.get("details", {}).get("error", {}).get("message", "")
                and retry_count < max_retry
            ):
                retry_count += 1
                print(f"[{retry_count}] 게시물 내용이 500자를 초과하여 재생성 시도합니다.")
                short_prompt = f"{prompt}\n\n(주의: 게시물 내용은 500자 이하로 요약해서 작성해줘.)"
                text = generate_thread_post(short_prompt)
                upload_result = upload_post(ACCESS_TOKEN, text)
            
            with open('upload_result.json','r', encoding='utf-8') as f:
                upload_result = json.load(f)
            
            print(upload_result.get('message'))
        else:
            print("[-] 액세스 토큰 만료 혹은 오류")
