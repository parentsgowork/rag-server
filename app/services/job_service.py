from app.models.jobSchemas import JobPosting, UserPreference
from app.services.crawl import crawl_all_jobs
from difflib import SequenceMatcher

CAREER_SYNONYMS = {
    "요양": ["요양보호사", "간병", "재가요양", "방문요양"],
    "청소": ["미화", "환경미화", "환경관리"],
    "운전": ["택시", "버스", "화물", "운전기사"],
    "경비": ["보안", "관리", "순찰"],
}


def is_similar(a: str, b: str, threshold: float = 0.6) -> bool:
    return SequenceMatcher(None, a, b).ratio() >= threshold


def is_career_match(user_input: str, title: str, career: str) -> bool:
    candidates = [user_input] + CAREER_SYNONYMS.get(user_input, [])
    for keyword in candidates:
        if keyword in title or keyword in career or is_similar(keyword, title):
            return True
    return "무관" in career


def filter_jobs(preference: UserPreference) -> list[JobPosting]:
    all_jobs = crawl_all_jobs()
    matched = []

    for job in all_jobs:
        try:
            title = job.get("title", "")
            region = job.get("region", "")
            work_type = job.get("work_type", "")
            career = job.get("career", "")
            education = job.get("education", "")

            if preference.region not in region and not region.startswith(
                preference.region
            ):
                continue

            if preference.education not in education and "학력무관" not in education:
                continue

            if not is_career_match(preference.career, title, career):
                continue

            if not any(wt in work_type for wt in preference.work_type):
                continue

            matched.append(JobPosting(**job))
        except Exception as e:
            print("❌ JobPosting 생성 실패:", job)
            print("에러:", e)

    print(f"[추천된 결과 수]: {len(matched)}개")
    return matched
