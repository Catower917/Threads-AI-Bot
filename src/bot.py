import os
import openai
import requests
import json
import random
from dotenv import load_dotenv
from src.prompt import get_prompt  # 기존 프롬프트 템플릿 사용

# 최신 권장사항에 따라 ChatOpenAI를 langchain_openai에서 임포트
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

# Google Serper Search API 임포트 (기사 검색용)
from langchain_community.utilities import GoogleSerperAPIWrapper


# .env 파일 로드
load_dotenv()

# 환경 변수 로드
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USER_ID = os.getenv("USER_ID")  # Threads 사용자 ID
SERPER_API_KEY = os.getenv("SERPER_API_KEY")  # Serper API 키

# OpenAI API 설정
openai.api_key = OPENAI_API_KEY
BASE_URL = "https://graph.threads.net/v1.0"

def upload_post(access_token: str, text: str, image_url: str = None):
    """
    Threads API를 사용하여 게시물을 업로드합니다.
    image_url이 제공되면 단일 게시물로 이미지와 텍스트를 함께 업로드합니다.
    """
    if not access_token or not text:
        return {"error": "Missing access token or text for post"}

    media_url = f"{BASE_URL}/{USER_ID}/threads"
    
    if image_url:
        payload = {
            'media_type': 'IMAGE',
            'image_url': image_url,
            'text': text,
            'access_token': access_token
        }
    else:
        payload = {
            'media_type': 'TEXT',
            'text': text,
            'access_token': access_token
        }
    
    response = requests.post(media_url, data=payload)
    container_id = response.json().get('id')
    if not container_id:
        return {"error": "Failed to create media container", "details": response.json()}

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

# 뉴스 검색 기반반
# def search_news(topic: str) -> tuple:
#     """
#     Serper 뉴스 검색 API를 사용하여 주제에 관한 최신 뉴스 10개를 검색하고,
#     그 중 무작위로 하나의 뉴스 항목을 선택하여 (title, snippet, imageUrl) 튜플을 반환합니다.
#     """
#     url = "https://google.serper.dev/news"
#     payload = json.dumps({
#          "q": topic,
#          "tbs": "qdr:w",  # 지난 한 주 동안의 뉴스
#          "num": 10
#     })
#     headers = {
#          "X-API-KEY": SERPER_API_KEY,
#          "Content-Type": "application/json"
#     }
#     response = requests.request("POST", url, headers=headers, data=payload)
#     if response.status_code == 200:
#         try:
#             data = response.json()
#             news_items = data.get("news", [])
#             if news_items:
#                 chosen = random.choice(news_items)
#                 title = chosen.get("title", "No Title")
#                 snippet = chosen.get("snippet", "No snippet")
#                 image_url = chosen.get("imageUrl", None)
#                 return title, snippet, image_url
#             else:
#                 print("No news items found.")
#                 return None
#         except Exception as e:
#             print("Error processing news search results:", e)
#             return None
#     else:
#         print("Serper news search failed:", response.text)
#         return None


def search_web(topic: str) -> str:
    """
    Google Serper Search API를 사용하여 주제에 관한 최신 텍스트 정보를 검색합니다.
    기존 함수를 그대로 사용합니다.
    """
    serper = GoogleSerperAPIWrapper(tbs="qdr:h", 
                                type="search", 
                                serper_api_key=SERPER_API_KEY,
                                k=20)
    result = serper.run(topic+" news")
    return result

def search_image(query: str) -> str:
    """
    Serper 이미지 검색 API를 사용하여 주제와 관련된 이미지 중
    무작위로 하나의 imageUrl을 반환합니다.
    """
    url = "https://google.serper.dev/images"
    payload = json.dumps({
         "q": query,
         "tbs": "qdr:h",
         "num": 10
    })
    headers = {
         "X-API-KEY": SERPER_API_KEY,
         "Content-Type": "application/json"
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        try:
            data = response.json()
            images = data.get("images", [])
            if images:
                chosen = random.choice(images)  # 무작위 선택
                return chosen.get("imageUrl")
        except Exception as e:
            print("이미지 검색 결과 처리 중 오류:", e)
            return None
    else:
        print("Serper 이미지 검색 실패:", response.text)
    return None



def generate_thread_post_chain(final_prompt: str) -> str:
    """
    RunnableSequence 스타일 체인을 사용하여 기존 프롬프트(final_prompt)를 기반으로 게시물 콘텐츠를 생성합니다.
    """
    prompt_template = ChatPromptTemplate.from_template(final_prompt)
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.8)
    # 체인 구성: 프롬프트 템플릿과 LLM을 연결합니다.
    chain = prompt_template | llm
    result = chain.invoke({"prompt": final_prompt})
    return result.content.strip()

def main():
    topics = ["AI Trend"]  # 영어 주제로 설정하여 글로벌 뉴스를 수집
    for topic in topics:
        # 기사 검색: Serper를 사용하여 텍스트 기사 검색 (원본 기사 내용)
        news = search_web(topic)
        print("검색된 기사 내용")
        print(news)
        # 이미지 검색: Serper 이미지 검색으로 첫 번째 이미지 URL 선택
        image_url = search_image("Ai")
        print("선택된 이미지 URL:")
        print(image_url)
        
        # 기존 prompt.py의 get_prompt를 사용하여 최종 프롬프트 생성 (요약된 뉴스 포함)
        final_prompt = get_prompt(topic, news)

        # LangChain 체인을 통해 게시물 내용 생성
        post_content = generate_thread_post_chain(final_prompt)
        print("게시물 내용:")
        print(post_content)
    
        if ACCESS_TOKEN:
            upload_result = upload_post(ACCESS_TOKEN, post_content, image_url=image_url)
            # 게시물 내용이 500자를 초과할 경우 재생성 (최대 3회)
            max_retry = 3
            retry_count = 0
            while (
                "error" in upload_result and
                "Param text must be at most 500 characters long." in upload_result.get("details", {}).get("error", {}).get("message", "")
                and retry_count < max_retry
            ):
                retry_count += 1
                print(f"[{retry_count}] 게시물 내용이 500자를 초과하여 재생성 시도합니다.")
                short_prompt = f"{final_prompt}\n\n(주의: 게시물 내용은 500자 이하로 요약해서 작성해줘.)"
                post_content = generate_thread_post_chain(short_prompt)
                upload_result = upload_post(ACCESS_TOKEN, post_content, image_url=image_url)
            
            print(upload_result.get('message'))
        else:
            print("[-] 액세스 토큰 만료 혹은 오류")

if __name__ == "__main__":
    main()




# def main():
#     topics = ["AI Trend"]  # 영어 주제로 설정하여 글로벌 뉴스를 수집
#     for topic in topics:
#         # 뉴스 검색: Serper 뉴스 검색 API를 사용하여 최신 뉴스 항목 중 무작위로 하나 선택
#         news_result = search_news(topic)
#         if news_result:
#             title, snippet, image_url = news_result
#             # 뉴스 텍스트를 간략하게 구성 (타이틀과 스니펫)
#             news = f"Title: {title}\nSnippet: {snippet}\n"
#         else:
#             news = "No news found."
#             image_url = None
        
#         print("선택된 뉴스 요약:")
#         print(news)
#         print("선택된 이미지 URL:", image_url)
        
#         # 기존 prompt.py의 get_prompt를 사용하여 최종 프롬프트 생성 (뉴스 요약 포함)
#         final_prompt = get_prompt(topic, news)
#         print("생성 프롬프트:")
#         print(final_prompt)
        
#         # LangChain 체인을 통해 게시물 내용 생성
#         post_content = generate_thread_post_chain(final_prompt)
#         print("생성된 게시물 내용:")
#         print(post_content)
    
#         if ACCESS_TOKEN:
#             upload_result = upload_post(ACCESS_TOKEN, post_content, image_url=image_url)
#             # 게시물 내용이 500자를 초과할 경우 재생성 (최대 3회)
#             max_retry = 3
#             retry_count = 0
#             while (
#                 "error" in upload_result and
#                 "Param text must be at most 500 characters long." in upload_result.get("details", {}).get("error", {}).get("message", "")
#                 and retry_count < max_retry
#             ):
#                 retry_count += 1
#                 print(f"[{retry_count}] 게시물 내용이 500자를 초과하여 재생성 시도합니다.")
#                 short_prompt = f"{final_prompt}\n\n(주의: 게시물 내용은 500자 이하로 요약해서 작성해줘.)"
#                 post_content = generate_thread_post_chain(short_prompt)
#                 upload_result = upload_post(ACCESS_TOKEN, post_content, image_url=image_url)
            
#             print(upload_result.get('message'))
#         else:
#             print("[-] 액세스 토큰 만료 혹은 오류")

# if __name__ == "__main__":
#     main()

