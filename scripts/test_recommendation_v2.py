#!/usr/bin/env python3
"""
빌드 추천 API v2 테스트 스크립트
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.database.db import get_db_session
from backend.database.models import Hero
from backend.recommendation.engine_v2 import RecommendationEngineV2


def test_recommendation_v2():
    """추천 엔진 v2 테스트"""
    print("=" * 80)
    print("빌드 추천 엔진 v2 테스트 (게임 메커니즘 기반)")
    print("=" * 80)

    with get_db_session() as db:
        # 첫 번째 영웅으로 테스트
        hero = db.query(Hero).first()

        if not hero:
            print("⚠ 데이터베이스에 영웅이 없습니다.")
            print("먼저 크롤러를 실행하여 데이터를 수집하세요:")
            print("  python scripts/crawl_all_data.py")
            return

        print(f"\n테스트 영웅: {hero.name} ({hero.talent})")
        print(f"God Type: {hero.god_type}")
        print("-" * 80)

        # 추천 엔진 v2 실행
        engine = RecommendationEngineV2(db)

        try:
            recommendation = engine.recommend_build(
                hero_id=hero.id,
                playstyle="Melee",
                max_skills=6,
                max_items=10
            )

            # 결과 출력
            print(f"\n빌드 타입: {recommendation['build_type']}")
            print(f"주 스탯: {recommendation['primary_stat']}")
            print(f"빌드 요약: {recommendation['build_summary']}")
            print(f"시너지 점수: {recommendation['synergy_score']}/100")

            # 추천 스킬
            print("\n" + "=" * 80)
            print("추천 스킬 (v2):")
            print("=" * 80)
            for i, skill in enumerate(recommendation['recommended_skills'], 1):
                print(f"\n[{i}] {skill['skill_name']}")
                print(f"    타입: {skill['skill_type']}")
                print(f"    데미지: {skill['damage_type'] or 'N/A'}")
                print(f"    DoT 스킬: {skill.get('is_dot', False)}")
                print(f"    Spell Burst 가능: {skill.get('is_spell_burst_compatible', False)}")
                print(f"    Combo: {skill.get('is_combo', False)}")
                print(f"    점수: {skill['score']}")
                print(f"    우선순위: {skill['priority']}")
                print(f"    이유: {skill['reason']}")

            # 추천 아이템
            print("\n" + "=" * 80)
            print("추천 아이템 (v2):")
            print("=" * 80)
            for i, item in enumerate(recommendation['recommended_items'], 1):
                print(f"\n[{i}] {item['item_name']}")
                print(f"    슬롯: {item['slot']}")
                print(f"    희귀도: {item['rarity'] or 'N/A'}")
                print(f"    스탯 타입: {item['stat_type'] or 'N/A'}")
                print(f"    세트: {item['set_name'] or 'N/A'}")
                print(f"    점수: {item['score']}")
                print(f"    이유: {item['reason']}")

            # 추천 재능 노드
            print("\n" + "=" * 80)
            print("추천 재능 노드 (v2):")
            print("=" * 80)
            for i, talent in enumerate(recommendation['recommended_talents'], 1):
                print(f"\n[{i}] {talent['node_name']}")
                print(f"    타입: {talent['node_type']}")
                print(f"    티어: {talent['tier'] or 'N/A'}")
                print(f"    God Class: {talent['god_class'] or 'N/A'}")
                print(f"    점수: {talent['score']}")
                print(f"    이유: {talent['reason']}")

            print("\n" + "=" * 80)
            print("✓ 추천 엔진 v2 테스트 완료!")
            print("=" * 80)

        except Exception as e:
            print(f"\n✗ 추천 실패: {e}")
            import traceback
            traceback.print_exc()


def test_all_heroes_v2():
    """모든 영웅에 대해 v2 추천 테스트"""
    print("\n" + "=" * 80)
    print("모든 영웅 v2 추천 테스트")
    print("=" * 80)

    with get_db_session() as db:
        heroes = db.query(Hero).limit(10).all()

        if not heroes:
            print("⚠ 데이터베이스에 영웅이 없습니다.")
            return

        engine = RecommendationEngineV2(db)

        for hero in heroes:
            try:
                recommendation = engine.recommend_build(
                    hero_id=hero.id,
                    max_skills=4,
                    max_items=6
                )

                print(f"\n{hero.name} ({hero.talent}) - {hero.god_type}")
                print(f"  빌드 타입: {recommendation['build_type']}")
                print(f"  주 스탯: {recommendation['primary_stat']}")
                print(f"  시너지 점수: {recommendation['synergy_score']}/100")
                print(f"  추천 스킬: {len(recommendation['recommended_skills'])}개")
                print(f"  추천 아이템: {len(recommendation['recommended_items'])}개")
                print(f"  요약: {recommendation['build_summary']}")

            except Exception as e:
                print(f"\n{hero.name}: 추천 실패 - {e}")

    print("\n" + "=" * 80)


def compare_v1_vs_v2():
    """v1과 v2 비교"""
    print("\n" + "=" * 80)
    print("v1 vs v2 비교")
    print("=" * 80)

    with get_db_session() as db:
        from backend.recommendation.engine import RecommendationEngine

        hero = db.query(Hero).first()
        if not hero:
            return

        engine_v1 = RecommendationEngine(db)
        engine_v2 = RecommendationEngineV2(db)

        rec_v1 = engine_v1.recommend_build(hero.id, max_skills=5, max_items=5)
        rec_v2 = engine_v2.recommend_build(hero.id, max_skills=5, max_items=5)

        print(f"\n영웅: {hero.name} ({hero.talent})")
        print("\n[v1 결과]")
        print(f"  시너지 점수: {rec_v1['synergy_score']}/100")
        print(f"  요약: {rec_v1['build_summary']}")

        print("\n[v2 결과]")
        print(f"  빌드 타입: {rec_v2['build_type']}")
        print(f"  시너지 점수: {rec_v2['synergy_score']}/100")
        print(f"  요약: {rec_v2['build_summary']}")

        print("\n개선사항:")
        score_diff = rec_v2['synergy_score'] - rec_v1['synergy_score']
        print(f"  - 시너지 점수: {score_diff:+.1f}점")
        print(f"  - 빌드 타입 자동 분석: {rec_v2['build_type']}")
        print(f"  - 게임 메커니즘 기반 스코어링 적용")


if __name__ == "__main__":
    test_recommendation_v2()
    test_all_heroes_v2()
    compare_v1_vs_v2()
