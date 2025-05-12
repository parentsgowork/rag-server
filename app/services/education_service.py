from app.core.config import settings
import requests
from app.models.eduSchemas import EducationBookmarkRequest
from app.db_models.education_info import EducationInfo as EducationInfoDB
from sqlalchemy.orm import Session
import xml.etree.ElementTree as ET
from app.models.eduSchemas import EducationInfo
from sqlalchemy.orm import Session

from app.db_models.education_info import EducationInfo as EducationInfoDB

API_KEY = settings.seoul_openapi_key
API_URL = settings.seoul_openapi_url

CATEGORY_KEYWORDS = {
    "디지털기초역량": ["디지털", "스마트폰", "컴퓨터", "정보화"],
    "사무행정실무": ["엑셀", "한글", "문서", "행정", "회계"],
    "전문기술자격증": ["자격증", "기술", "정보처리", "전산"],
    "서비스 직무교육": ["서비스", "고객", "의사소통", "응대"],
}


def fetch_education_data():
    url = f"{API_URL}/{API_KEY}/xml/FiftyPotalEduInfo/1/100/"
    response = requests.get(url)
    return response.content


def parse_education_xml(xml_data, category):
    root = ET.fromstring(xml_data)
    rows = root.findall(".//row")
    keywords = CATEGORY_KEYWORDS.get(category, [])

    results = []
    for row in rows:
        title = row.findtext("LCT_NM", "")
        if any(keyword in title for keyword in keywords):
            edu = EducationInfo(
                title=title,
                reg_start_date=row.findtext("REG_STDE", "미정"),
                reg_end_date=row.findtext("REG_EDDE", "미정"),
                course_start_date=row.findtext("CR_STDE", "미정"),
                course_end_date=row.findtext("CR_EDDE", "미정"),
                hour=row.findtext("HR", "시간 미정"),
                status=row.findtext("LCT_STAT", "상태 미정"),
                url=row.findtext("CR_URL", "#"),
            )
            results.append(edu)

    return results


def save_bookmarked_education(data: EducationBookmarkRequest, db: Session):
    for item in data.bookmarks:
        edu = EducationInfoDB(user_id=data.user_id, title=item.title, url=item.url)
        db.add(edu)
    db.commit()
    return {"message": "교육 정보 북마크 성공."}
