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
