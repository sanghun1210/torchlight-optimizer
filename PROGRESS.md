# 프로젝트 진행 상황

## 완료된 작업 (2025-12-13)

### Phase 1: 데이터 크롤링 - 진행 중

#### ✅ 완료
1. **프로젝트 구조 및 기본 설정**
   - 데이터베이스 스키마 설계 (7개 테이블)
   - SQLAlchemy 모델 구현 (`backend/database/models.py`)
   - 데이터베이스 연결 설정 (`backend/database/db.py`)
   - 베이스 크롤러 구현 (`backend/crawler/base_crawler.py`)

2. **스킬 크롤러 v2 개선 완료** ⭐
   - **파일**: `backend/crawler/skills_crawler_v2.py`
   - **개선 내용**:
     - ✅ 태그 추출 (Mobility, Attack, Melee, Physical 등)
     - ✅ 데미지 타입 추출 (Physical, Fire, Cold, Lightning, Erosion, Chaos)
     - ✅ 마나 코스트 추출
     - ✅ 쿨다운 추출
     - ✅ **설명(Description) 추출 수정** - HTML 구조 분석 후 올바른 파싱 로직 구현
   - **결과**: 모든 스킬 정보가 정상적으로 추출됨 (샘플 3개 테스트 완료)

3. **영웅 크롤러 v2 개선 완료** ⭐
   - **파일**: `backend/crawler/heroes_crawler_v2.py`
   - **개선 내용**:
     - ✅ 개별 영웅/재능 페이지 방문
     - ✅ `god_type` 추출 (Berserker, Divineshot 등)
     - ✅ 영웅 이름 추출 (Rehan, Carino 등)
     - ✅ `description` 추출 및 정리 ("God|Name" 접두사 제거)
   - **결과**: 모든 영웅 정보가 정상적으로 추출됨 (샘플 3개 테스트 완료)

4. **레전더리 아이템 크롤러 v2 개선 완료** ⭐
   - **파일**: `backend/crawler/legendary_items_crawler_v2.py`
   - **개선 내용**:
     - ✅ 조부모 div 구조 분석 (`flex-grow-1` div에서 정보 추출)
     - ✅ `required_level` 추출 (Require lv X 패턴)
     - ✅ `special_effects` 추출 (모든 스탯/효과 라인)
     - ✅ 아이템 타입 및 슬롯 자동 식별
   - **결과**: 모든 아이템 정보가 정상적으로 추출됨 (샘플 5개 테스트 완료)

#### 🔧 주요 버그 수정
1. **URL 생성 버그 수정** (`base_crawler.py:93`)
   - 문제: `https://tlidb.comLeap_Attack` (슬래시 누락)
   - 수정: 상대 URL 앞에 슬래시가 없으면 자동 추가

2. **데이터베이스 스키마 수정** (`models.py:18`)
   - 문제: `heroes.name` UNIQUE 제약 충돌 (같은 영웅이 여러 재능 보유)
   - 수정: `heroes.talent`을 UNIQUE로 변경

3. **스킬 설명 파싱 로직 수정** (`skills_crawler_v2.py:199-210`)
   - 문제: HTML 구조 오해로 설명 추출 실패
   - 수정: `simple_div.parent.find_next_sibling()` 사용 (조부모가 아닌 부모의 다음 형제)

## 다음 단계 추천

### 옵션 1: 전체 스킬 데이터 수집 (추천) ⭐
**예상 시간**: 10-15분
**설명**: 개선된 스킬 크롤러로 모든 카테고리의 스킬 수집
```bash
source .venv/bin/activate
python -m backend.crawler.skills_crawler_v2
```
**결과**:
- `data/skills_v2.json` - 전체 스킬 데이터 (JSON)
- 데이터베이스에 완전한 스킬 정보 저장

### 옵션 2: 아이템 크롤러 개선
**예상 시간**: 1-2시간
**설명**: 레전더리 아이템의 상세 정보 추출 로직 구현
**작업 내용**:
- 개별 아이템 페이지 방문
- `special_effects` (특수 효과) 추출
- `required_level` (요구 레벨) 추출
- 아이템 세트 효과 추출

### 옵션 3: 영웅 크롤러 개선
**예상 시간**: 1시간
**설명**: 영웅의 상세 정보 추출 로직 구현
**작업 내용**:
- `god_type` (신 타입) 추출
- `description` (영웅 설명) 추출
- 재능별 특성 추출

### 옵션 4: Phase 2 프로토타입 시작
**예상 시간**: 3-4시간
**설명**: 현재 데이터로 FastAPI 백엔드 프로토타입 구축
**작업 내용**:
- FastAPI 앱 설정
- 기본 API 엔드포인트 구현
  - `GET /heroes` - 영웅 목록
  - `GET /skills` - 스킬 목록
  - `GET /items` - 아이템 목록
- 간단한 추천 로직 프로토타입

## 현재 데이터 상태

### 수집된 데이터
- ✅ 영웅: 24개 재능 (기본 정보)
- ✅ 스킬: 139개 (기본 정보) → **v2로 개선 완료**
- ✅ 레전더리 아이템: 316개 (기본 정보)

### 데이터 품질
| 항목 | 이름 | 타입 | 이미지 | 태그 | 설명 | 특수효과 |
|------|------|------|--------|------|------|----------|
| 영웅 | ✅ | ⚠️ | ✅ | - | ⚠️ | - |
| 스킬 | ✅ | ✅ | ✅ | ✅ | ✅ | - |
| 아이템 | ✅ | ✅ | ✅ | - | ⚠️ | ⚠️ |

## 파일 구조
```
torchlight-optimizer/
├── backend/
│   ├── crawler/
│   │   ├── base_crawler.py          # ✅ 기본 크롤러 (버그 수정됨)
│   │   ├── skills_crawler_v2.py     # ✅ 스킬 크롤러 v2 (개선 완료)
│   │   ├── heroes_crawler.py        # ⚠️ 개선 필요
│   │   └── legendary_items_crawler.py # ⚠️ 개선 필요
│   └── database/
│       ├── models.py                # ✅ 데이터베이스 모델 (수정됨)
│       └── db.py                    # ✅ DB 연결
├── scripts/
│   ├── test_skill_crawler_v2.py     # 스킬 크롤러 테스트
│   ├── debug_skill_page.py          # HTML 구조 디버깅
│   ├── debug_skill_page_v2.py       # 상세 구조 분석
│   ├── debug_description.py         # 설명 추출 디버깅
│   └── test_skill_debug.py          # 디버그 로깅 테스트
├── data/
│   ├── skills_v2_sample.json        # ✅ 샘플 스킬 데이터 (완벽)
│   ├── heroes.json                  # 영웅 데이터
│   ├── skills.json                  # 구버전 스킬 데이터
│   └── legendary_items.json         # 아이템 데이터
└── ARCHITECTURE.md                  # 시스템 설계 문서
```

## 추천 진행 순서

1. **단기** (오늘/내일):
   - ✅ 스킬 크롤러 v2 개선 완료
   - 🔄 전체 스킬 데이터 수집 (옵션 1)
   - 🔄 아이템 크롤러 개선 (옵션 2)

2. **중기** (이번 주):
   - 영웅 크롤러 개선 (옵션 3)
   - 전체 데이터 재수집
   - FastAPI 백엔드 프로토타입 시작 (옵션 4)

3. **장기** (다음 주 이후):
   - Phase 2: 추천 알고리즘 구현
   - Phase 3: 프론트엔드 개발
   - Phase 4: 배포
