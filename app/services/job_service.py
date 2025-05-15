import json
import requests
import xml.etree.ElementTree as ET
from sqlalchemy.orm import Session
from app.db_models.user import User
from app.core.config import settings
from app.models.jobSchemas import JobRecommendation
from openai import OpenAI
from difflib import SequenceMatcher
from app.utils.field_ailias_map import SIMILAR_JOB_MAP


REGION_KR_MAP = {
    "SEOUL": "서울",
    "GYEONGGI": "경기",
    "INCHEON": "인천",
    "GANGWON": "강원",
    "DAEJEON": "대전",
    "SEJONG": "세종",
    "CHUNGBUK": "충북",
}


def is_similar(a: str, b: str) -> bool:
    return SequenceMatcher(None, a, b).ratio() > 0.3


def get_career_code(career: int):
    if career == 0:
        return "J01301"
    elif career > 0:
        return "J01302"
    return "J01300"


def check_similarity_and_filter(root, job_keyword, user_region_kr, job_aliases):
    filtered_jobs = []

    print("===== 포함 기반 매칭 필터링 시작 =====")
    for row in root.findall(".//row"):
        title = row.findtext("JO_SJ", "").strip()
        jobcode = row.findtext("JOBCODE_NM", "").strip()
        region = row.findtext("WORK_PARAR_BASS_ADRES_CN", "").strip()

        # alias가 title 또는 jobcode 중 하나에 포함되면 True
        keyword_included = any(
            alias in title or alias in jobcode for alias in job_aliases
        )

        region_match = user_region_kr in region or is_similar(user_region_kr, region)

        if keyword_included and region_match:
            job_dict = {child.tag: child.text for child in row}
            filtered_jobs.append(job_dict)
            print(f"매칭된 공고: {title} | {jobcode} | {region}")
        # else:
        # print(f"제외된 공고: {title} | {jobcode} | {region}")

    print(f"최종 필터링 결과: {len(filtered_jobs)}건")
    return filtered_jobs


def select_top_jobs_by_gpt_and_descriptions(user, jobs: list[dict]) -> list[dict]:
    prompt = (
        f"당신은 취업 도우미입니다. 아래는 사용자의 기본 정보와 공고 리스트입니다.\n\n"
        f"[사용자 정보]\n"
        f"- 직무: {user.job}\n"
        f"- 지역: {REGION_KR_MAP.get(user.region, '')}\n"
        f"- 학력: {user.final_edu.value}\n"
        f"- 경력: {user.career}년\n\n"
        f"[지침]\n"
        f"1. 사용자에게 가장 적합한 공고 3개만 선택하세요.\n"
        f"2. 각 공고마다 직무 특징을 1~2문장으로 요약한 'description'을 작성해주세요.\n"
        f"3. 아래 형식처럼 JSON 배열로 반환하세요:\n"
        f'[{{"jo_regist_no": "공고번호", "description": "요약 설명"}}]\n\n'
        f"[공고 목록]\n"
    )

    for job in jobs:
        prompt += (
            f"- 공고번호: {job['JO_REGIST_NO']}, 회사: {job['CMPNY_NM']}, 직무명: {job['JOBCODE_NM']}, 제목: {job['JO_SJ']}\n"
            f"  내용: {job.get('DTY_CN', '').strip()[:300]}...\n"
        )

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)

        selected_jobs = []
        for item in parsed:
            job = next(
                (j for j in jobs if j["JO_REGIST_NO"] == item["jo_regist_no"]), None
            )
            if job:
                job["description"] = (
                    item.get("description") or job.get("DTY_CN", "")[:200]
                )
                selected_jobs.append(job)

        return selected_jobs

    except Exception as e:
        print(f"GPT 오류 발생 (description 포함): {e}")
        for j in jobs[:3]:
            j["description"] = j.get("DTY_CN", "")[:200]
        return jobs[:3]


def recommend_jobs(user_id: int, db: Session) -> list[JobRecommendation]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    user_region_kr = REGION_KR_MAP.get(user.region, "")
    job_keyword = user.job.strip()
    job_aliases = SIMILAR_JOB_MAP.get(job_keyword, [job_keyword])

    print(f"User job: {user.job}, region: {user.region}")
    print(f"Region mapped: {user_region_kr}")

    url = f"http://openapi.seoul.go.kr:8088/{settings.seoul_openapi_key}/xml/GetJobInfo/1/1000/"
    response = requests.get(url)
    if response.status_code != 200:
        return []

    root = ET.fromstring(response.content)
    filtered_jobs = check_similarity_and_filter(
        root, job_keyword, user_region_kr, job_aliases
    )

    if not filtered_jobs:
        return []

    filtered_jobs = filtered_jobs[:5]  # GPT에 넘길 후보 5개 제한
    top_jobs = select_top_jobs_by_gpt_and_descriptions(user, filtered_jobs)

    recommendations = []
    for job in top_jobs:
        recommendations.append(
            JobRecommendation(
                jo_reqst_no=job.get("JO_REQST_NO", ""),
                jo_regist_no=job.get("JO_REGIST_NO", ""),
                company_name=job.get("CMPNY_NM", ""),
                job_title=job.get("JO_SJ", ""),
                description=job.get("description", "설명을 불러올 수 없습니다."),
                deadline=job.get("RCEPT_CLOS_NM", ""),
                location=job.get("WORK_PARAR_BASS_ADRES_CN", ""),
                pay=job.get("HOPE_WAGE", ""),
                registration_date=job.get("JO_REG_DT", ""),
                time=job.get("WORK_TIME_NM", ""),
            )
        )

    return recommendations
