# 답변에서 나이대, 업종 추출하는 모듈
import json
from langchain.chat_models import ChatOpenAI
from app.core.config import settings

def extract_user_profile(answer_text: str) -> dict:
    system_prompt = """
너는 사용자의 재취업 가능성 분석 결과에서 '나이대'와 '업종/직군'을 추출하는 도우미야.
다음과 같은 JSON 형태로 반환해야 해:

{
  "age_group": "50대",
  "field": "IT"
}

만약 특정 정보가 없다면 null로 표시해.
"""
    chat = ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model="gpt-4-1106-preview"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": answer_text}
    ]

    response = chat.invoke(messages)
    json_result = json.loads(response.content)

    return json_result