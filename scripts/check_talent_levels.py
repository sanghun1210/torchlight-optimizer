#!/usr/bin/env python3
"""
수집된 재능 레벨 데이터 확인 스크립트
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.database.db import get_db_session
from backend.database.models import TalentLevel
import json


def check_talent_levels():
    """수집된 재능 레벨 데이터 확인"""
    print("=" * 80)
    print("수집된 재능 레벨 데이터 확인")
    print("=" * 80)

    with get_db_session() as db:
        all_levels = db.query(TalentLevel).all()

        if not all_levels:
            print("\n⚠ 데이터베이스에 재능 레벨 데이터가 없습니다.")
            return

        print(f"\n총 {len(all_levels)}개의 재능 레벨 효과 수집됨\n")

        # 재능별로 그룹화
        from collections import defaultdict
        talent_groups = defaultdict(list)

        for level in all_levels:
            talent_groups[level.talent_name].append(level)

        # 재능별 출력
        for talent_name in sorted(talent_groups.keys()):
            levels = talent_groups[talent_name]
            print(f"\n{'='*80}")
            print(f"재능: {talent_name}")
            print(f"{'='*80}")
            print(f"수집된 레벨 효과: {len(levels)}개\n")

            # 레벨순으로 정렬
            levels.sort(key=lambda x: x.level)

            for lvl in levels:
                print(f"  [{lvl.level}레벨] {lvl.effect_name}")

                # 메커니즘 파싱
                try:
                    mechanics = json.loads(lvl.mechanics) if lvl.mechanics else []
                    if mechanics:
                        print(f"    메커니즘: {', '.join(mechanics)}")
                except:
                    pass

                # 설명 일부 출력 (처음 100자)
                desc_preview = lvl.effect_description[:100] + "..." if len(lvl.effect_description) > 100 else lvl.effect_description
                print(f"    설명: {desc_preview}")
                print()

        # 특별히 Anger 상세 출력
        print("\n" + "=" * 80)
        print("🔥 Anger 재능 상세 정보 (Burst 특화)")
        print("=" * 80)

        anger_levels = db.query(TalentLevel).filter(
            TalentLevel.talent_name == 'Anger'
        ).order_by(TalentLevel.level).all()

        if anger_levels:
            for lvl in anger_levels:
                print(f"\n[레벨 {lvl.level}] {lvl.effect_name}")
                print(f"설명: {lvl.effect_description}")

                try:
                    mechanics = json.loads(lvl.mechanics) if lvl.mechanics else []
                    if mechanics:
                        print(f"메커니즘 태그: {', '.join(mechanics)}")
                except:
                    pass
        else:
            print("\n⚠ Anger 재능 데이터를 찾을 수 없습니다.")

        # 60레벨 효과 (중요한 전환점) 확인
        print("\n" + "=" * 80)
        print("⭐ 60레벨 효과 (모든 재능)")
        print("=" * 80)

        level_60_effects = db.query(TalentLevel).filter(
            TalentLevel.level == 60
        ).order_by(TalentLevel.talent_name).all()

        if level_60_effects:
            for effect in level_60_effects:
                print(f"\n{effect.talent_name} - {effect.effect_name}")
                desc_preview = effect.effect_description[:150] + "..." if len(effect.effect_description) > 150 else effect.effect_description
                print(f"  {desc_preview}")
        else:
            print("\n⚠ 60레벨 효과를 찾을 수 없습니다.")


if __name__ == "__main__":
    check_talent_levels()
