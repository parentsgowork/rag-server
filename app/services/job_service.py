from app.core.config import settings
import requests
import xml.etree.ElementTree as ET
from app.models.jobSchemas import JobSummary
import openai

# 카테고리명 직종 코드 매핑
CATEGORY_CODE_MAP = {
    "사무직": "024",
    "서비스직": "050",
    "기술직": "121",
    "판매직": "062",
}

API_KEY = settings.JOB_INFO_KEY
API_URL = settings.JOB_INFO_URL
OPENAI_API_KEY = settings.OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def fetch_job_data(category: str, region=None, career=None, education=None, empTp=None):
    code = CATEGORY_CODE_MAP.get(category)
    if not code:
        return {"error": f"[{category}]는 지원되지 않는 직종입니다."}

    params = {
        "authKey": API_KEY,
        "callTp": "L",
        "returnType": "XML",
        "startPage": 1,
        "display": 5,  # 처리 속도 고려해 5건 제한
        "occupation": code,
        "pfPreferential": "B",
    }

    if region:
        params["region"] = region
    if career:
        params["career"] = career
        params["minCareerM"] = 0
        params["maxCareerM"] = 999
    if education:
        params["education"] = education
    if empTp:
        params["empTp"] = empTp

    response = requests.get(API_URL, params=params)
    print("호출된 URL:", response.url)
    print("응답 내용 일부:", response.text[:500])
    if response.status_code != 200:
        return {"error": "공공 API 호출 실패"}

    jobs = parse_job_xml(response.content)

    if not jobs:
        return {"message": "조회된 구직 정보가 없습니다."}

    # 각 항목마다 GPT 설명 추가
    summaries = [summarize_job(job) for job in jobs]

    return {"count": len(summaries), "results": summaries}


def parse_job_xml(xml_data):
    root = ET.fromstring(xml_data)
    rows = root.findall(".//wanted")

    results = []
    for row in rows:
        job = {
            "title": row.findtext("title", "제목 없음"),
            "company": row.findtext("company", ""),
            "sal_type": row.findtext("salTpNm", ""),
            "salary": row.findtext("sal", ""),
            "region": row.findtext("region", ""),
            "work_type": row.findtext("holidayTpNm", ""),
            "education": row.findtext("minEdubg", ""),
            "career": row.findtext("career", ""),
            "reg_date": row.findtext("regDt", ""),
            "close_date": row.findtext("closeDt", ""),
        }
        results.append(job)

    return results


def summarize_job(job: dict) -> JobSummary:
    info = (
        f"채용 제목: {job['title']}\n"
        f"회사명: {job['company']}\n"
        f"임금형태: {job['sal_type']}\n"
        f"급여: {job['salary']}\n"
        f"근무지역: {job['region']}\n"
        f"근무형태: {job['work_type']}\n"
        f"최소학력: {job['education']}\n"
        f"경력 요건: {job['career']}\n"
        f"등록일: {job['reg_date']}\n"
        f"마감일: {job['close_date']}\n"
    )

    prompt = (
        "다음은 채용 공고의 상세 정보입니다.\n"
        "내용을 기반으로, 구직자가 이해할 수 있도록 객관적으로 설명해 주세요.\n"
        "추측, 조언, 의견 없이 사실만 정리해주세요.\n\n"
        f"{info}"
    )

    # 디버깅용
    print(info)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        max_tokens=300,
        messages=[
            {
                "role": "system",
                "content": "당신은 채용 공고 정보를 설명해주는 AI입니다.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    summary = response.choices[0].message["content"]
    return JobSummary(title=job["title"], description=summary)
