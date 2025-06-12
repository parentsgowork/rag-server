# 다시 일해! (Parents go work!)
정년퇴직자 및 중장년층을 대상으로 한 **RAG 기반 챗봇** 구직 지원 서비스
<br/>
### 개발 기간
`2025.04.12`-`2025.05.12` 
## 프로젝트 아키텍처
![image](https://github.com/user-attachments/assets/0de773c0-a2cf-4749-98c3-aae46de9b827)
## 주요 기능
1. 서울시 일자리포털 채용정보 기반 사용자 맞춤 채용정보 추천
2. 중장년층 취업률과 직종 별 취업자 수 통계 기반으로 한 재취업 가능성 분석
3. 서울특별시 50플러스 포털 교육정보 및 고용노동부 고령자 맞춤 정책/복지 관련 RAG 검색 및 AI 교육 추천
4. 대화형 AI 자기소개서 기능
## 사용데이터
| 데이터 보유기관 | 데이터명/출처 |
| --- | --- |
| 서울특별시 | 서울시 일자리플러스센터 채용정보 |
| 고용노동부 | 고령자 고용률현황 |
| 고용노동부 | 고령자 계속고용장려금 |
|  | 고령자 고용지원금 |
|  | 중장년 내일센터 |
|  | 폴리텍 신중년 특화과정 |
|  | 중장년 경력지원제 |
|  | 재취업지원서비스 시행지원 |
|  | 생애경력설계서비스 |
| 서울특별시 | 서울시 50플러스포털 교육정보 |

## 파일 구조

```bash
rag-server/
├── app/
│   ├── api/                         # FastAPI 엔드포인트 (라우팅)
│   │   ├── __init__.py
│   │   └── routes.py

│   ├── core/                        # 환경 설정 및 DB 연결
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── db.py

│   ├── db_models/                   # SQLAlchemy 기반 DB 모델 정의
│   │   ├── __init__.py
│   │   ├── education.py
│   │   ├── policy.py
│   │   └── user.py

│   ├── models/                      # Pydantic 요청/응답 모델 (Schemas)
│   │   ├── __init__.py
│   │   ├── eduSchemas.py
│   │   ├── policySchemas.py
│   │   └── reempSchemas.py

│   ├── services/                    # 서비스 로직 (비즈니스 로직 처리)
│   │   ├── __init__.py
│   │   ├── rag_service.py
│   │   ├── data_ingest.py
│   │   ├── data_ingest_policy.py
│   │   ├── education_service.py
│   │   ├── policy_service.py
│   │   └── reemp_service.py

│   ├── utils/                       # 보조 유틸리티 모듈
│   │   ├── __init__.py
│   │   ├── db_test.py
│   │   ├── profile_extractor.py
│   │   └── test_pinecone_inspect.py

├── .env                             # 환경변수 설정 파일
├── requirements.txt                 # 의존 패키지 목록
├── venv/                            # 가상환경
└── README.md

```

## Git Convention

- **[FEAT]**: 새로운 기능 추가
- **[FIX]**: 버그 수정
- **[REFACT]**: 코드 리팩토링 (기능 변화 없음)
- **[STYLE]**: 코드 스타일 변경 (포맷팅, 세미콜론 추가/제거 등)
- **[DOCS]**: 문서 변경
- **[TEST]**: 테스트 추가 또는 수정
- **[CHORE]**: 기타 수정 (빌드, CI/CD, 패키지 관리 등)
- **[DEPLOY]**: 배포 관련 작업 (배포 자동화, 배포 스크립트 수정 등)
