"""
스킬 데이터 확인 스크립트
한글 데이터가 제대로 수집되었는지 확인
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.models import Skill

# DB 연결
db_path = project_root / "data" / "torchlight.db"
engine = create_engine(f"sqlite:///{db_path}")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # 최근 업데이트된 스킬 5개 조회
    recent_skills = db.query(Skill).order_by(Skill.id.desc()).limit(5).all()

    print("=" * 80)
    print("최근 수집된 스킬 데이터 확인")
    print("=" * 80)

    for i, skill in enumerate(recent_skills, 1):
        print(f"\n{'='*80}")
        print(f"[{i}] {skill.name} (ID: {skill.id})")
        print(f"{'='*80}")
        print(f"타입: {skill.type}")
        print(f"데미지 타입: {skill.damage_type}")
        print(f"태그: {skill.tags}")
        print(f"\n설명 (처음 500자):")
        print("-" * 80)
        desc = skill.description if skill.description else "설명 없음"
        print(desc[:500])
        if len(desc) > 500:
            print(f"\n... (총 {len(desc)}자)")
        print("-" * 80)

        # 한글 포함 여부 체크
        has_korean = any('\uac00' <= char <= '\ud7a3' for char in desc)
        has_sections = "===" in desc

        print(f"\n✓ 한글 포함: {'예' if has_korean else '아니오'}")
        print(f"✓ 섹션 구분: {'예 (새 형식)' if has_sections else '아니오 (기존 형식)'}")

    # 통계
    print("\n" + "=" * 80)
    print("전체 스킬 통계")
    print("=" * 80)

    total = db.query(Skill).count()
    print(f"총 스킬 개수: {total}")

    # 설명이 있는 스킬
    with_desc = db.query(Skill).filter(Skill.description != None).filter(Skill.description != "").count()
    print(f"설명이 있는 스킬: {with_desc} ({with_desc/total*100:.1f}%)")

    # 한글이 포함된 스킬 샘플링 (100개 샘플)
    sample_skills = db.query(Skill).filter(Skill.description != None).limit(100).all()
    korean_count = sum(1 for s in sample_skills if s.description and any('\uac00' <= char <= '\ud7a3' for char in s.description))
    print(f"한글 포함 스킬 (100개 샘플): {korean_count}/100")

    # 새 형식(섹션 구분) 스킬
    section_count = sum(1 for s in sample_skills if s.description and "===" in s.description)
    print(f"섹션 구분된 설명 (100개 샘플): {section_count}/100")

finally:
    db.close()
