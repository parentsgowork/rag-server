import requests
import xml.etree.ElementTree as ET
from sqlalchemy.orm import Session
from app.db_models.user import User
from app.core.config import settings
from app.models.jobSchemas import JobRecommendation
from openai import OpenAI

REGION_KR_MAP = {
    "SEOUL": "서울",
    "GYEONGGI": "경기",
    "INCHEON": "인천",
    "GANGWON": "강원",
    "DAEJEON": "대전",
    "SEJONG": "세종",
    "CHUNGBUK": "충북",
}

EDU_CODE_MAP = {
    "HIGH_SCHOOL": "J00106",
    "ASSOCIATE": "J00108",
    "BACHELOR": "J00110",
    "MASTER": "J00114",
    "DOCTOR": "J00114",
}


def get_career_code(career: int):
    if career == 0:
        return "J01301"
    elif career > 0:
        return "J01302"
    return "J01300"


def select_top_jobs_by_gpt(user, jobs: list[dict]) -> list[dict]:
    """GPT를 통해 사용자에게 가장 적합한 상위 3개 공고를 선택"""
    prompt = (
        f"사용자 정보:\n"
        f"- 직무: {user.job}\n"
        f"- 지역: {REGION_KR_MAP.get(user.region.name, '')}\n"
        f"- 학력: {user.final_edu.name}\n"
        f"- 경력: {user.career}년\n\n"
        f"아래는 채용 공고 목록입니다. 사용자에게 가장 적합한 3개 공고를 골라 JSON 배열 형태로 반환해주세요. "
        f"각 항목은 'JO_REGIST_NO'만 포함하고, 주관적인 판단 없이 정보 기반으로 판단해주세요.\n\n"
    )

    for job in jobs:
        prompt += f"- 공고번호: {job['JO_REGIST_NO']}, 직무: {job['JO_SJ']}, 지역: {job['WORK_PARAR_BASS_ADRES_CN']}, 경력조건: {job['CAREER_CND_NM']}, 학력조건: {job['ACDMCR_NM']}\n"

    prompt += '\n결과 예시:\n["K12345", "K23456", "K34567"]'

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    try:
        selected_ids = eval(response.choices[0].message.content.strip())
        return [job for job in jobs if job["JO_REGIST_NO"] in selected_ids]
    except Exception:
        return jobs[:3]


def generate_description_gpt(job_title, company_name, job_content, user_job):
    prompt = (
        f"사용자의 관심 직무는 '{user_job}'입니다. "
        f"다음은 {company_name}의 '{job_title}' 직무에 대한 상세 설명입니다:\n"
        f"{job_content}\n\n"
        f"이 정보를 바탕으로 우대사항과 직무의 특징을 요약해 주세요. 감정이나 판단 없이 설명만 해주세요."
    )

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def recommend_jobs(user_id: int, db: Session) -> list[JobRecommendation]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    user_region_kr = REGION_KR_MAP.get(user.region.name, "")
    job_keyword = user.job.strip()

    url = f"http://openapi.seoul.go.kr:8088/{settings.seoul_openapi_key}/xml/GetJobInfo/1/200/"
    response = requests.get(url)
    if response.status_code != 200:
        return []

    root = ET.fromstring(response.content)
    filtered_jobs = []

    for row in root.findall(".//row"):
        title = row.findtext("JO_SJ", "").strip()
        if job_keyword not in title:
            continue

        region_text = row.findtext("WORK_PARAR_BASS_ADRES_CN", "")
        if user_region_kr not in region_text:
            continue

        job_dict = {child.tag: child.text for child in row}
        filtered_jobs.append(job_dict)

    # GPT가 최적의 공고 3개 선택
    top_jobs = select_top_jobs_by_gpt(user, filtered_jobs)

    recommendations = []
    for job in top_jobs:
        description = generate_description_gpt(
            job_title=job.get("JO_SJ", ""),
            company_name=job.get("CMPNY_NM", ""),
            job_content=job.get("DTY_CN", ""),
            user_job=user.job.strip(),
        )

        recommendations.append(
            JobRecommendation(
                jo_reqst_no=job.get("JO_REQST_NO", ""),
                jo_regist_no=job.get("JO_REGIST_NO", ""),
                company_name=job.get("CMPNY_NM", ""),
                job_title=job.get("JO_SJ", ""),
                description=description,
                deadline=job.get("RCEPT_CLOS_NM", ""),
                location=job.get("WORK_PARAR_BASS_ADRES_CN", ""),
                pay=job.get("HOPE_WAGE", ""),
                registration_date=job.get("JO_REG_DT", ""),
                time=job.get("WORK_TIME_NM", ""),
            )
        )

    return recommendations
