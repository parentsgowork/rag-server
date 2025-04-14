## 파일 구조

```bash
rag_chatbot/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py            # FastAPI 엔드포인트 모음
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py            # dotenv 읽기 및 설정 관리
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag_service.py       # LangChain, OpenAI, Pinecone RAG 서비스 모듈
│   │   └── data_ingest.py       # api/CSV -> Pinecone 벡터업로드 처리
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic Request/Response 모델
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py           # 공용 유틸 함수 모음
│   │
│   └── main.py                  # FastAPI 앱 실행 파일
│
├── .env                         # 환경변수 설정
├── requirements.txt             # 패키지 목록
├── venv/                        # 가상환경 (gitignore에 포함)
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
