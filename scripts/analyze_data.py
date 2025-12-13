#!/usr/bin/env python3
"""
수집된 데이터 분석 스크립트
"""
import json
import sys
from pathlib import Path

# 프로젝트 루트 경로
project_root = Path(__file__).parent.parent
data_dir = project_root / "data"

def analyze_heroes():
    """영웅 데이터 분석"""
    with open(data_dir / "heroes.json", "r", encoding="utf-8") as f:
        heroes = json.load(f)

    print(f"📊 영웅 데이터: {len(heroes)}개")
    print(f"   - 고유 영웅: {len(set(h['name'] for h in heroes))}명")
    print(f"   - God type Unknown: {sum(1 for h in heroes if h['god_type'] == 'Unknown')}개")
    print(f"   - 설명 없음: {sum(1 for h in heroes if not h['description'])}개")
    print()

    # 샘플
    print("   샘플 (5개):")
    for hero in heroes[:5]:
        print(f"     - {hero['name']} ({hero['talent']})")
    print()

def analyze_skills():
    """스킬 데이터 분석"""
    with open(data_dir / "skills.json", "r", encoding="utf-8") as f:
        skills = json.load(f)

    print(f"📊 스킬 데이터: {len(skills)}개")

    # 타입별 분류
    skill_types = {}
    for s in skills:
        skill_types[s['type']] = skill_types.get(s['type'], 0) + 1

    for stype, count in sorted(skill_types.items()):
        print(f"   - {stype}: {count}개")

    print(f"   - 태그 없음: {sum(1 for s in skills if s['tags'] == '[]')}개")
    print(f"   - 설명 없음: {sum(1 for s in skills if not s['description'])}개")
    print()

    # 샘플
    print("   샘플 (5개):")
    for skill in skills[:5]:
        print(f"     - {skill['name']} [{skill['type']}]")
    print()

def analyze_items():
    """레전드 아이템 데이터 분석"""
    with open(data_dir / "legendary_items.json", "r", encoding="utf-8") as f:
        items = json.load(f)

    print(f"📊 레전드 아이템: {len(items)}개")

    # 타입별 분류
    item_types = {}
    for i in items:
        item_types[i['type']] = item_types.get(i['type'], 0) + 1

    for itype, count in sorted(item_types.items()):
        print(f"   - {itype}: {count}개")

    effects_count = sum(1 for i in items if json.loads(i['special_effects']))
    print(f"   - 효과 있음: {effects_count}개")
    print(f"   - 효과 없음: {len(items) - effects_count}개")
    print()

    # 샘플
    print("   샘플 (5개):")
    for item in items[:5]:
        effects = json.loads(item['special_effects'])
        effect_count = len(effects) if effects else 0
        print(f"     - {item['name']} [{item['type']}] - 효과: {effect_count}개")
    print()

def main():
    print("=" * 70)
    print(" 수집된 데이터 분석 보고서")
    print("=" * 70)
    print()

    analyze_heroes()
    analyze_skills()
    analyze_items()

    print("=" * 70)

if __name__ == "__main__":
    main()
