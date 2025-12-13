# Torchlight Infinite 자동 최적 세팅 추천기 - 아키텍처 문서

## 1. 프로젝트 개요

### 목적
토치라이트 인피니트 게임의 직업(영웅)을 선택하면, 해당 직업에 최적화된 스킬과 아이템 조합을 자동으로 추천하는 웹 애플리케이션

### 핵심 기능
- 22개 영웅 중 선택
- 스킬 시너지 분석 기반 추천
- 아이템 세트 효과 고려
- 메타 트렌드 반영

---

## 2. 기술 스택

### Backend
- **Language**: Python 3.10+
- **Web Framework**: FastAPI
- **Database**: SQLite
- **Web Scraping**: BeautifulSoup4, Requests
- **ORM**: SQLAlchemy

### Frontend
- **Framework**: HTML5, CSS3, JavaScript (Vanilla)
- **Optional**: React (추후 고려)

### DevOps
- **Version Control**: Git
- **Deployment**: Docker (선택사항)

---

## 3. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Web UI)                    │
│  - 영웅 선택 인터페이스                                    │
│  - 추천 결과 표시                                         │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────┐
│              FastAPI Backend Server                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │  API Layer (main.py)                             │   │
│  │  - GET /heroes (영웅 목록)                        │   │
│  │  - GET /recommend/{hero_id} (추천)               │   │
│  └─────────────────┬───────────────────────────────┘   │
│                    │                                     │
│  ┌─────────────────▼───────────────────────────────┐   │
│  │  Recommender Engine (engine.py)                  │   │
│  │  - 스킬 시너지 분석                                │   │
│  │  - 아이템 세트 효과 계산                           │   │
│  │  - 메타 트렌드 가중치 적용                         │   │
│  └─────────────────┬───────────────────────────────┘   │
│                    │                                     │
│  ┌─────────────────▼───────────────────────────────┐   │
│  │  Database Layer (models.py, db.py)               │   │
│  │  - SQLAlchemy ORM                                │   │
│  │  - 데이터 접근 로직                                │   │
│  └─────────────────┬───────────────────────────────┘   │
└────────────────────┼─────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              SQLite Database (torchlight.db)             │
│  - Heroes (영웅 정보)                                     │
│  - Skills (스킬 정보)                                     │
│  - Items (아이템 정보)                                    │
│  - Synergies (시너지 관계)                                │
│  - Meta Builds (메타 빌드 데이터)                         │
└──────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│         Crawler Module (별도 실행)                        │
│  - tlidb.com 크롤링                                       │
│  - 데이터 파싱 및 정제                                     │
│  - DB에 저장                                              │
└─────────────────────────────────────────────────────────┘
```

---

## 4. 데이터베이스 스키마 설계

### 4.1 Heroes (영웅)
```sql
CREATE TABLE heroes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    god_type TEXT NOT NULL,  -- God of Might, Wisdom, etc.
    talent TEXT NOT NULL,     -- Brave, Onslaughter, etc.
    description TEXT,
    image_url TEXT,
    popularity_score REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 Skills (스킬)
```sql
CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- Active, Support, Passive, etc.
    description TEXT,
    tags TEXT,  -- JSON array: ["AoE", "DoT", "Melee"]
    damage_type TEXT,  -- Physical, Fire, Lightning, etc.
    cooldown REAL,
    mana_cost INTEGER,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.3 Items (아이템)
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- Helmet, Armor, Weapon, etc.
    slot TEXT NOT NULL,  -- Head, Chest, MainHand, etc.
    rarity TEXT,  -- Common, Rare, Legendary, etc.
    stat_type TEXT,  -- STR, DEX, INT
    base_stats TEXT,  -- JSON: {"armor": 100, "health": 50}
    special_effects TEXT,  -- JSON array
    set_name TEXT,  -- 세트 아이템인 경우
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.4 Hero_Skills (영웅-스킬 연관)
```sql
CREATE TABLE hero_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hero_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    recommended_level INTEGER,  -- 추천 레벨
    priority INTEGER,  -- 우선순위 (1=최우선)
    FOREIGN KEY (hero_id) REFERENCES heroes(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id),
    UNIQUE(hero_id, skill_id)
);
```

### 4.5 Skill_Synergies (스킬 시너지)
```sql
CREATE TABLE skill_synergies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_a_id INTEGER NOT NULL,
    skill_b_id INTEGER NOT NULL,
    synergy_score REAL NOT NULL,  -- 0.0 ~ 1.0
    synergy_type TEXT,  -- damage_boost, cooldown_reduction, etc.
    description TEXT,
    FOREIGN KEY (skill_a_id) REFERENCES skills(id),
    FOREIGN KEY (skill_b_id) REFERENCES skills(id)
);
```

### 4.6 Item_Sets (아이템 세트)
```sql
CREATE TABLE item_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    set_name TEXT NOT NULL UNIQUE,
    pieces_required INTEGER NOT NULL,
    set_bonus_2 TEXT,  -- 2피스 효과
    set_bonus_4 TEXT,  -- 4피스 효과
    set_bonus_6 TEXT,  -- 6피스 효과
    description TEXT
);
```

### 4.7 Meta_Builds (메타 빌드)
```sql
CREATE TABLE meta_builds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hero_id INTEGER NOT NULL,
    build_name TEXT NOT NULL,
    season TEXT,  -- S1, S2, etc.
    popularity_rank INTEGER,
    skill_combination TEXT,  -- JSON array of skill IDs
    item_recommendation TEXT,  -- JSON array of item IDs
    playstyle TEXT,  -- Melee, Ranged, Tank, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hero_id) REFERENCES heroes(id)
);
```

---

## 5. 디렉토리 구조

```
torchlight-optimizer/
├── backend/
│   ├── __init__.py
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── tlidb_crawler.py      # 메인 크롤러
│   │   ├── heroes_crawler.py     # 영웅 데이터 크롤링
│   │   ├── skills_crawler.py     # 스킬 데이터 크롤링
│   │   ├── items_crawler.py      # 아이템 데이터 크롤링
│   │   └── data_parser.py        # HTML 파싱 유틸리티
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py             # SQLAlchemy 모델
│   │   ├── db.py                 # DB 연결 및 세션 관리
│   │   └── schema.sql            # 스키마 정의 (참고용)
│   ├── recommender/
│   │   ├── __init__.py
│   │   ├── engine.py             # 메인 추천 엔진
│   │   ├── synergy_analyzer.py   # 스킬 시너지 분석
│   │   ├── item_optimizer.py     # 아이템 최적화
│   │   └── meta_analyzer.py      # 메타 분석
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI 메인
│   │   ├── routes.py             # API 라우트
│   │   └── schemas.py            # Pydantic 스키마
│   └── config.py                 # 설정 파일
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       └── app.js
│   └── templates/
│       └── index.html
├── data/
│   └── torchlight.db             # SQLite DB 파일
├── tests/
│   ├── test_crawler.py
│   ├── test_recommender.py
│   └── test_api.py
├── scripts/
│   └── run_crawler.py            # 크롤러 실행 스크립트
├── requirements.txt
├── .gitignore
├── ARCHITECTURE.md               # 이 문서
└── README.md
```

---

## 6. 추천 알고리즘 로직

### 6.1 스킬 시너지 분석
1. 선택된 영웅의 기본 추천 스킬 로드
2. 스킬 간 시너지 점수 계산
3. 시너지 점수가 높은 조합 우선 추천

**시너지 점수 계산식:**
```
synergy_score = (base_synergy * 0.4) + (damage_boost * 0.3) + (meta_weight * 0.3)
```

### 6.2 아이템 세트 효과
1. 영웅의 stat_type에 맞는 아이템 필터링
2. 세트 효과가 있는 아이템 우선 추천
3. 스킬 조합과 호환되는 아이템 매칭

### 6.3 메타 트렌드 가중치
1. 현재 시즌의 인기 빌드 데이터 로드
2. 인기도에 따라 추천 순위 조정
3. 최신 데이터일수록 높은 가중치

---

## 7. API 엔드포인트 설계

### 7.1 영웅 관련
- `GET /api/heroes` - 모든 영웅 목록
- `GET /api/heroes/{hero_id}` - 특정 영웅 상세 정보
- `GET /api/heroes/gods/{god_type}` - 특정 신 계열 영웅 목록

### 7.2 추천 관련
- `POST /api/recommend` - 빌드 추천 요청
  ```json
  {
    "hero_id": 1,
    "preferences": {
      "playstyle": "ranged",
      "focus": "damage"  // damage, survival, utility
    }
  }
  ```
- `GET /api/recommend/{hero_id}` - 기본 추천 (인기 빌드)

### 7.3 데이터 조회
- `GET /api/skills` - 스킬 목록
- `GET /api/items` - 아이템 목록
- `GET /api/meta-builds` - 메타 빌드 목록

---

## 8. 크롤링 전략

### 8.1 타겟 페이지
1. **영웅**: `https://tlidb.com/heroes/`
2. **스킬**: `https://tlidb.com/skills/` (카테고리별)
3. **아이템**: `https://tlidb.com/items/` (타입별)

### 8.2 크롤링 순서
1. 영웅 데이터 (기본 정보)
2. 스킬 데이터 (전체 스킬)
3. 영웅-스킬 연관 (각 영웅 상세 페이지)
4. 아이템 데이터
5. 세트 아이템 관계

### 8.3 주의사항
- Rate limiting (요청 간 0.5~1초 대기)
- User-Agent 설정
- 실패 시 재시도 로직
- 증분 업데이트 지원

---

## 9. 단계별 구현 계획

### Phase 1: 데이터 수집 (Week 1)
- [ ] 데이터베이스 스키마 구현
- [ ] 기본 크롤러 프레임워크
- [ ] 영웅 데이터 크롤링
- [ ] 스킬 데이터 크롤링
- [ ] 아이템 데이터 크롤링

### Phase 2: 백엔드 구현 (Week 2)
- [ ] FastAPI 기본 구조
- [ ] 데이터베이스 모델 (SQLAlchemy)
- [ ] 기본 API 엔드포인트
- [ ] 단순 추천 로직 (인기 기반)

### Phase 3: 추천 엔진 (Week 3)
- [ ] 스킬 시너지 분석 알고리즘
- [ ] 아이템 세트 최적화
- [ ] 메타 트렌드 반영
- [ ] 추천 엔진 통합

### Phase 4: 프론트엔드 (Week 4)
- [ ] 기본 UI 레이아웃
- [ ] 영웅 선택 인터페이스
- [ ] 추천 결과 표시
- [ ] 반응형 디자인

### Phase 5: 테스트 및 배포
- [ ] 유닛 테스트
- [ ] 통합 테스트
- [ ] 문서화
- [ ] 배포 준비

---

## 10. 확장 가능성

### 향후 기능
- 사용자 계정 시스템
- 커스텀 빌드 저장/공유
- 빌드 비교 기능
- 실시간 메타 분석
- 커뮤니티 평가 시스템

### 성능 최적화
- Redis 캐싱
- API 응답 캐싱
- 데이터베이스 인덱싱
- 비동기 처리 확대

---

## 11. 참고사항

### 데이터 출처
- **Primary**: https://tlidb.com/ (팬 운영 위키)
- **Note**: 베타 테스트 데이터 기반, 정기적 업데이트 필요

### 라이선스 고려사항
- tlidb.com: "fan-made and not affiliated with XD"
- 데이터 사용 시 출처 표기 권장
- 상업적 이용 금지 (개인/학습 목적)
