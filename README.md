# Torchlight Infinite 자동 최적 세팅 추천기

토치라이트 인피니트 게임의 직업(영웅)을 선택하면 최적화된 스킬과 아이템 조합을 자동으로 추천해주는 웹 애플리케이션

## 주요 기능

- **영웅 선택**: 22개의 플레이 가능한 영웅 중 선택
- **스킬 시너지 분석**: 스킬 간 상호작용을 분석하여 최적 조합 추천
- **아이템 세트 효과**: 세트 아이템 효과를 고려한 장비 추천
- **메타 트렌드 반영**: 현재 시즌의 인기 빌드 데이터 반영

## 기술 스택

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy
- **Database**: SQLite
- **Crawler**: BeautifulSoup4, Requests
- **Frontend**: HTML5, CSS3, JavaScript

## 프로젝트 구조

```
torchlight-optimizer/
├── backend/           # 백엔드 코드
│   ├── crawler/       # 웹 크롤링 모듈
│   ├── database/      # DB 모델 및 연결
│   ├── recommender/   # 추천 엔진
│   └── api/           # FastAPI 서버
├── frontend/          # 프론트엔드 코드
│   ├── static/        # CSS, JS
│   └── templates/     # HTML 템플릿
├── data/              # 데이터 저장소
└── scripts/           # 유틸리티 스크립트
```

## 시작하기

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 데이터 크롤링

```bash
python scripts/run_crawler.py
```

### 3. 서버 실행

```bash
uvicorn backend.api.main:app --reload
```

브라우저에서 `http://localhost:8000` 접속

## 개발 로드맵

### Phase 1: 데이터 수집 ✅ (예정)
- [x] 아키텍처 설계
- [ ] 데이터베이스 스키마 구현
- [ ] 웹 크롤러 개발
- [ ] 초기 데이터 수집

### Phase 2: 백엔드 구현 (예정)
- [ ] FastAPI 서버 구축
- [ ] API 엔드포인트 구현
- [ ] 기본 추천 로직

### Phase 3: 추천 엔진 (예정)
- [ ] 스킬 시너지 분석
- [ ] 아이템 최적화 알고리즘
- [ ] 메타 분석 통합

### Phase 4: 프론트엔드 (예정)
- [ ] UI/UX 디자인
- [ ] 영웅 선택 인터페이스
- [ ] 추천 결과 시각화

## 문서

- [아키텍처 문서](ARCHITECTURE.md) - 상세한 시스템 설계 및 구현 계획

## 데이터 출처

- [TLI DB](https://tlidb.com/) - Torchlight: Infinite 팬 운영 위키

**Note**: 이 프로젝트는 개인/학습 목적으로 제작되었으며, XD Games와 공식적으로 관련이 없습니다.

## 라이선스

개인/학습 목적 전용 - 상업적 이용 금지

## 기여

이슈 및 풀 리퀘스트 환영합니다!
