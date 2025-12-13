#!/usr/bin/env python3
"""
빌드 추천 API 테스트 스크립트
"""
import sys
from pathlib import Path
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.database.db import get_db_session
from backend.database.models import Hero
from backend.recommendation.engine import RecommendationEngine


def test_recommendation_engine():
    """추천 엔진 직접 테스트"""
    print("=" * 70)
    print("빌드 추천 엔진 테스트")
    print("=" * 70)

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
        print("-" * 70)

        # 추천 엔진 실행
        engine = RecommendationEngine(db)

        try:
            recommendation = engine.recommend_build(
                hero_id=hero.id,
                playstyle="Melee",
                max_skills=5,
                max_items=8
            )

            # 결과 출력
            print(f"\n빌드 요약: {recommendation['build_summary']}")
            print(f"시너지 점수: {recommendation['synergy_score']}/100")

            # 추천 스킬
            print("\n" + "=" * 70)
            print("추천 스킬:")
            print("=" * 70)
            for i, skill in enumerate(recommendation['recommended_skills'], 1):
                print(f"\n[{i}] {skill['skill_name']}")
                print(f"    타입: {skill['skill_type']}")
                print(f"    데미지: {skill['damage_type'] or 'N/A'}")
                print(f"    점수: {skill['score']}")
                print(f"    이유: {skill['reason']}")

            # 추천 아이템
            print("\n" + "=" * 70)
            print("추천 아이템:")
            print("=" * 70)
            for i, item in enumerate(recommendation['recommended_items'], 1):
                print(f"\n[{i}] {item['item_name']}")
                print(f"    슬롯: {item['slot']}")
                print(f"    희귀도: {item['rarity'] or 'N/A'}")
                print(f"    세트: {item['set_name'] or 'N/A'}")
                print(f"    점수: {item['score']}")
                print(f"    이유: {item['reason']}")

            # 추천 재능 노드
            print("\n" + "=" * 70)
            print("추천 재능 노드:")
            print("=" * 70)
            for i, talent in enumerate(recommendation['recommended_talents'], 1):
                print(f"\n[{i}] {talent['node_name']}")
                print(f"    타입: {talent['node_type']}")
                print(f"    티어: {talent['tier'] or 'N/A'}")
                print(f"    점수: {talent['score']}")
                print(f"    이유: {talent['reason']}")

            print("\n" + "=" * 70)
            print("✓ 추천 엔진 테스트 완료!")
            print("=" * 70)

        except Exception as e:
            print(f"\n✗ 추천 실패: {e}")
            import traceback
            traceback.print_exc()


def test_all_heroes():
    """모든 영웅에 대해 빠른 추천 테스트"""
    print("\n" + "=" * 70)
    print("모든 영웅 빠른 추천 테스트")
    print("=" * 70)

    with get_db_session() as db:
        heroes = db.query(Hero).limit(5).all()

        if not heroes:
            print("⚠ 데이터베이스에 영웅이 없습니다.")
            return

        engine = RecommendationEngine(db)

        for hero in heroes:
            try:
                recommendation = engine.recommend_build(
                    hero_id=hero.id,
                    max_skills=3,
                    max_items=3
                )

                print(f"\n{hero.name} ({hero.talent})")
                print(f"  시너지 점수: {recommendation['synergy_score']}/100")
                print(f"  추천 스킬: {len(recommendation['recommended_skills'])}개")
                print(f"  추천 아이템: {len(recommendation['recommended_items'])}개")
                print(f"  요약: {recommendation['build_summary']}")

            except Exception as e:
                print(f"\n{hero.name}: 추천 실패 - {e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    test_recommendation_engine()
    test_all_heroes()
