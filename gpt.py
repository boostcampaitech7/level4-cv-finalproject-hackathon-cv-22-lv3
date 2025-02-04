import openai
import pandas as p
from main import main_pipline
openai.api_key = ""
# 예시: main_pipeline() 실행 후 결과 받기
comparison_df, original_prediction, optimized_prediction_value = main_pipline()

def get_solution_from_llm(comparison_df):
    # comparison_df가 DataFrame이 아니라 문자열이면, 바로 사용
    if isinstance(comparison_df, str):
        df_json = comparison_df
    else:
        df_json = comparison_df.to_json(orient="records", force_ascii=False, indent=2)
    
    prompt = f"""
    아래는 모델의 feature optimization 결과를 담은 JSON 데이터입니다:
    
    {df_json}
    
    이 데이터를 바탕으로, Prescriptive AI로써 고객에게 Target의 값을 최적화하기 위한 solution을 제공해주세요.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a data scientist expert."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        temperature=0.7
    )
    
    solution = response['choices'][0]['message']['content']
    return solution

# GPT API를 사용하여 solution 받기
solution = get_solution_from_llm(comparison_df)
print("LLM이 제시한 솔루션:")
print(solution)


