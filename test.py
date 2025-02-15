# Google Serper Search API 임포트 (기사 검색용)
from langchain_community.utilities import GoogleSerperAPIWrapper
import os
# .env 파일 로드
from dotenv import load_dotenv
load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")  # Serper API 키


serper = GoogleSerperAPIWrapper(tbs="qdr:h", 
                                type="search", 
                                serper_api_key=SERPER_API_KEY,
                                k=20)
result = serper.run("Ai trend")
print(result)