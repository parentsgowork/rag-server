import json
from langchain_openai import ChatOpenAI
from app.core.config import settings

def extract_user_profile(answer_text: str) -> dict:
    prompt = f"""
너는 사용자의 재취업 가능성 분석 결과를 기반으로 '나이대'와 '업종/직군'을 추출하는 도우미야.

- 반드시 JSON 형태로만 답변해.
- 텍스트 설명을 추가하지 마.
- 예시:
{{
  "age_group": "50대",
  "field": "IT"
}}

특정 정보가 없으면 null로 작성해.

분석 결과:
{answer_text}
"""

    chat = ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model="gpt-4-1106-preview"
    )

    response = chat.invoke(prompt)  # 그냥 하나의 긴 텍스트
    text = response.content

    # ✅ 추가: 만약 이미 dict처럼 오면 json.loads 안 하고 바로 처리
    if isinstance(text, dict):
        return text

    try:
        json_result = json.loads(text)
    except json.JSONDecodeError:
        print(f"❌ JSON 파싱 실패, 받은 답변:\n{text}")
        return {"age_group": None, "field": None}

    return json_result
