# En
# SNS Threads AI Bot

This project is an AI Bot that automatically uploads posts to Meta Threads.  
Key features include:

- **Registering a Meta Developer App and setting up Redirect URLs**
- **Requesting and managing access tokens**
- **Automation using external schedulers**
- **Automatically generating post content using LLM (GPT-4)**

---

## 1. Registering a Meta Developer App and Setting Redirect URLs

1. **App Registration**  
   - Register a new app at the [Meta Developer Page](https://developers.facebook.com/).
   - After registration, obtain the Client ID and Client Secret.

2. **Configure Redirect URL**  
   - In the app settings, register the OAuth Redirect URL.  
     Example: `https://your-app-domain/callback`
   - Set the required scopes (e.g., `threads_basic`).

---

## 2. Requesting Access Tokens

1. **OAuth Authentication Flow**  
   - Redirect to the Meta Threads authentication page via the `/login` endpoint.
   - Once the user completes authentication, Meta will send a code to the redirect URL (`/callback`).

2. **Token Exchange**  
   - Use the code received at the `/callback` endpoint to request a short-lived access token.
   - Exchange the short-lived token for a long-lived access token and store it in your environment variables.

3. **Setting up Environment Variables (.env)**  
   Create an actual environment variable file (.env) based on the `.env.example` file:
   ```dotenv
   APP_ID=your_app_id
   APP_SECRET=your_app_secret
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key
   USER_ID=your_user_id
   ACCESS_TOKEN=your_long_lived_access_token
   PORT=5000



# Ko
# SNS Threads AI Bot

이 프로젝트는 Meta Threads에 자동으로 게시물을 업로드하는 AI Bot입니다.  
주요 기능은 다음과 같습니다:

- **Meta 개발자 앱 등록 및 리다이렉션 URL 설정**
- **액세스 토큰 요청 및 관리**
- **외부 스케줄러를 활용한 자동화**
- **LLM(GPT-4) 기반 게시물 내용 자동 작성**

---

## 1. Meta 개발자 앱 등록 및 리다이렉션 URL 설정

1. **앱 등록**  
   - [Meta 개발자 페이지](https://developers.facebook.com/)에서 새 앱을 등록합니다.
   - 앱 등록 후, 클라이언트 ID와 클라이언트 시크릿을 발급받습니다.

2. **리다이렉션 URL 설정**  
   - 앱 설정에서 OAuth 리다이렉션 URL을 등록합니다.  
     예: `https://your-app-domain/callback`  
   - 필요한 스코프(예: `threads_basic`)를 설정합니다.

---

## 2. 액세스 토큰 요청

1. **OAuth 인증 흐름**  
   - `/login` 엔드포인트를 통해 Meta Threads 인증 페이지로 리다이렉트합니다.
   - 사용자가 인증을 완료하면, Meta에서 리다이렉션 URL(`/callback`)로 코드가 전달됩니다.

2. **토큰 교환**  
   - `/callback` 엔드포인트에서 받은 코드를 이용해 짧은 액세스 토큰을 요청합니다.
   - 짧은 토큰을 장기 액세스 토큰으로 교환한 후, 환경 변수에 저장합니다.

3. **환경 변수 설정 (.env)**  
   `.env.example` 파일을 참고하여 실제 환경 변수 파일(.env)을 생성합니다:
   ```dotenv
   APP_ID=your_app_id
   APP_SECRET=your_app_secret
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key
   USER_ID=your_user_id
   ACCESS_TOKEN=your_long_lived_access_token
   PORT=5000