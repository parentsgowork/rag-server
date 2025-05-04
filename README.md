## 파일 구조

```bash
rag-server/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py                  # FastAPI 엔드포인트 모음
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                  # 환경변수 및 설정 관리
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py                # 재취업 가능성 스키마
│   │   ├── eduSchemas.py             # 교육 정보 관련 스키마
│   │   └── policySchemas.py          # 정책 정보 관련 스키마
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag_service.py            # 재취업 가능성 판단
│   │   ├── data_ingest.py            # 일반 데이터 벡터화 업로드
│   │   ├── data_ingest_policy.py     # 정책 PDF 병합 및 벡터화 업로드
│   │   ├── education_service.py      # 맞춤형 교육 정보 추천 서비스
│   │   └── policy_service.py         # 복지/정책 추천 서비스
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── profile_extractor.py      # 사용자 재취업 프로필 추출기
│   │   └── test_pinecone_inspect.py  # Pinecone 벡터 확인용 유틸
│
├── .env                               # 환경변수 설정 파일
├── requirements.txt                   # 의존 패키지 목록
├── venv/                              # 가상환경 (gitignore 대상)
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
