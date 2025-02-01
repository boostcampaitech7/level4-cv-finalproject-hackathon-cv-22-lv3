import openai
import os
import time
from main import main_pipline
from openai.error import RateLimitError, OpenAIError  # 예외 클래스 임포트
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, filename='app.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 환경 변수에서 API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("API 키가 환경 변수에 설정되지 않았습니다.")

openai.api_key = OPENAI_API_KEY

# 사용할 모델 지정
model = "text-embedding-3-small"

# 분석 파이프라인 실행
comparison_df, origin, predict = main_pipline()

# 데이터프레임 요약 (필요 시 수정)
if hasattr(comparison_df, 'describe'):
    comparison_summary = comparison_df.describe().to_string()
else:
    comparison_summary = str(comparison_df)


# print(comparison_summary)

# 분석 프롬프트 생성
analysis_prompt = f"""
다음 텍스트를 분석해주세요. Prescriptive AI처럼 답변해주세요:
result 요약: {comparison_summary}
"""

# 메시지 구성
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    },
    {
        "role": "user",
        "content": analysis_prompt
    }
]

# 재시도 로직 설정 (Exponential Backoff)
max_retries = 5
retry_delay = 1  # 초기 지연 시간 (초)

for attempt in range(max_retries):
    try:
        # ChatCompletion API 호출
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=150  # 응답 최대 토큰 수 설정 (필요 시 조정)
        )
        analysis_answer = response.choices[0].message.content
        print("=== 분석 결과 ===")
        print(analysis_answer)
        logging.info("API 호출 성공.")
        break  # 성공 시 루프 종료
    except RateLimitError:
        logging.warning(f"Rate limit exceeded on attempt {attempt + 1}. Retrying in {retry_delay} seconds...")
        print(f"Rate limit exceeded. Attempt {attempt + 1} of {max_retries}. Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
        retry_delay *= 2  # 지연 시간 증가
    except OpenAIError as e:
        logging.error(f"An OpenAI error occurred: {e}")
        print(f"An OpenAI error occurred: {e}")
        break
else:
    logging.error("Failed to get a response after multiple attempts due to rate limits.")
    print("Failed to get a response after multiple attempts due to rate limits.")