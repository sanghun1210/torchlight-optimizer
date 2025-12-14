# Project Context - Torchlight Optimizer

## 현재 상태 (2024-12-14)
✅ **Mechanics-Aware AI 추천 시스템 완료**
- Backend: OpenAI API 연동 + 게임 메커니즘 분석 통합
- Frontend: React UI with AI/Rule-Based 토글
- 하이브리드 시스템: AI + Rule-Based 병행
- 메커니즘 분석: 스킬/아이템 자동 분석 및 시너지 계산

## 시스템 아키텍처

### Backend (FastAPI + OpenAI + Mechanics Analyzer)
```
User Request
    ↓
FastAPI Endpoint (/api/recommendations/ai/build/{hero_id})
    ↓
Context Builder → SQLite DB (Heroes, Skills, Items, Talents)
    ↓                ↓
    ↓         Mechanics Analyzer (스킬/아이템 메커니즘 분석)
    ↓                ↓
    ↓         • DoT vs Hit 분류
    ↓         • Ailment 매핑 (Fire→Ignite, Erosion→Wilt 등)
    ↓         • 시너지 점수 계산
    ↓         • 빌드 타입 결정
    ↓                ↓
    └────────────────┘
    ↓
AI Service → OpenAI API (gpt-4o-mini with game mechanics knowledge)
    ↓
JSON Response (skills, items, synergy_explanation, playstyle_tips)
```

### Frontend (React + Vite)
```
User Interface
    ↓
HeroSelector (AI/v2 토글)
    ↓
API Service Layer (axios)
    ↓
Conditional Rendering:
  - AI → AIBuildRecommendation (purple theme)
  - v2 → BuildRecommendation (green theme)
```

## 핵심 파일 구조

```
backend/
├── main.py                          # FastAPI app + load_dotenv()
├── recommendation/
│   ├── engine_v2.py                 # Rule-based (유지)
│   ├── context_builder.py           # DB → Prompt 변환 + Mechanics 통합
│   ├── mechanics_analyzer.py        # 🆕 게임 메커니즘 분석기
│   └── ai_service.py                # OpenAI API 호출 (mechanics 지식 포함)
└── api/routes/
    └── recommendations.py           # /api/recommendations/*

frontend/src/
├── services/api.js                  # API 호출 레이어
├── components/
│   ├── HeroSelector.jsx             # AI/v2 토글 + Playstyle 입력
│   ├── AIBuildRecommendation.jsx    # AI 결과 표시
│   └── BuildRecommendation.jsx      # v2 결과 표시
└── App.jsx                          # 메인 앱

.env                                 # OPENAI_API_KEY 설정
```

## 실행 방법

### Backend
```bash
source .venv/bin/activate
uvicorn backend.main:app --reload  # http://localhost:8000
```

### Frontend
```bash
cd frontend
npm run dev  # http://localhost:3000
```

### 필수 설정
- `.env` 파일에 `OPENAI_API_KEY` 설정 필수
- `backend/main.py`에서 `load_dotenv()` 자동 로드

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/heroes` | 영웅 목록 |
| GET | `/api/recommendations/build/{hero_id}` | Rule-based 추천 (v2) |
| GET | `/api/recommendations/ai/build/{hero_id}` | AI 추천 ✨ |
| GET | `/api/recommendations/ai/quick/{hero_id}` | 빠른 AI 추천 |

## 주요 기능

### AI 추천 (Mechanics-Aware) 🆕
- **Input:** hero_id, playstyle (optional)
- **Output:**
  - `recommended_skills`: AI가 선택한 스킬 + 이유
  - `recommended_items`: AI가 선택한 아이템 + 이유
  - `synergy_explanation`: 시너지 분석 설명
  - `playstyle_tips`: 플레이 팁 리스트
  - `ai_metadata`: 토큰 사용량

**메커니즘 분석 기능:**
- 스킬 자동 분류: DoT / Hit / Hybrid
- Ailment 자동 매핑: Physical→Trauma, Fire→Ignite, Erosion→Wilt
- 시너지 점수 계산: 스킬-아이템 메커니즘 매칭
- 빌드 타입 결정: 스킬 조합 기반 빌드 스타일 추론
- 플레이 팁 자동 생성: 빌드 타입에 맞는 전략 제공

### Rule-Based 추천 (v2)
- **Input:** hero_id, playstyle, focus
- **Output:**
  - `recommended_skills`: 점수 기반 스킬 추천
  - `recommended_items`: 점수 기반 아이템 추천
  - `synergy_score`: 시너지 점수 (0-100)

## 설계 원칙

1. **데이터 무결성**: AI는 DB 데이터만 사용 (환각 방지)
2. **메커니즘 기반**: 게임 메커니즘(DoT, Hit, Ailment) 자동 분석 및 적용
3. **하이브리드**: AI와 Rule-based 병행 제공
4. **토큰 효율**: Context Builder로 관련 데이터만 선별
5. **타입 안전성**: 모든 Python 함수에 타입 힌트
6. **테스트 주도**: 메커니즘 분석기 단위 테스트 완료

## 다음 단계 (Optional)

- [ ] 캐싱: AI 응답 캐싱으로 비용 절감
- [ ] 사용자 피드백: 추천 결과 평가 기능
- [ ] 멀티 모델: GPT-4o vs GPT-4o-mini 선택 가능
- [ ] 빌드 히스토리: 사용자별 추천 기록
- [ ] A/B 테스트: AI vs Rule-based 성능 비교

## 기술 스택

**Backend:**
- Python 3.12, FastAPI, SQLAlchemy
- OpenAI API (gpt-4o-mini)
- python-dotenv (환경 변수)

**Frontend:**
- React 18, Vite
- Axios (API 통신)

**Database:**
- SQLite (로컬 개발)

## 테스트

### 메커니즘 통합 테스트
```bash
source .venv/bin/activate
python scripts/test_mechanics_integration.py
```

**테스트 결과 (2024-12-14):**
- ✅ Mechanics Analyzer: 스킬 분류 및 추천 스탯 생성
- ✅ Context Builder: MechanicsAnalyzer 통합
- ✅ Build Suggestions: 빌드 타입 자동 결정
- ✅ Synergy Calculation: DoT 빌드 + DoT 아이템 = 80점
- ✅ Synergy Penalty: DoT 빌드 + Crit 아이템 = -5점

## 참고 문서
- API 문서: http://localhost:8000/docs
- CLAUDE.md: 개발자 가이드
- README.md: 프로젝트 개요
- docs/mechanics_guide.md: 핵심 게임 메커니즘 가이드
