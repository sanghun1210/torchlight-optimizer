"""
Test Script: Mechanics-Aware Recommendation System Integration
메커니즘 분석 통합 테스트
"""
import os
import sys
from pathlib import Path

# Add backend to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.models import Base
from backend.recommendation.context_builder import ContextBuilder
from backend.recommendation.mechanics_analyzer import MechanicsAnalyzer


def test_mechanics_analyzer():
    """메커니즘 분석기 단독 테스트"""
    print("=" * 60)
    print("TEST 1: Mechanics Analyzer - Skill Analysis")
    print("=" * 60)

    analyzer = MechanicsAnalyzer()

    # 테스트 스킬 데이터
    test_skills = [
        {
            "id": 1,
            "name": "Fireball",
            "damage_type": "Fire",
            "tags": ["Spell", "AoE"],
            "description": "Launches a fireball that deals damage over time through ignite"
        },
        {
            "id": 2,
            "name": "Rapid Strike",
            "damage_type": "Physical",
            "tags": ["Attack", "Multistrike"],
            "description": "Strikes rapidly with increased attack speed"
        },
        {
            "id": 3,
            "name": "Poison Arrow",
            "damage_type": "Erosion",
            "tags": ["Ranged", "DoT"],
            "description": "Shoots arrows that apply wilt stacks over time"
        }
    ]

    for skill in test_skills:
        print(f"\n📋 Analyzing: {skill['name']}")
        analysis = analyzer.analyze_skill_mechanics(skill)

        print(f"  Build Style: {analysis['build_style']}")
        print(f"  Damage Type: {analysis['damage_type']}")
        print(f"  Ailment: {analysis['ailment']}")
        print(f"  Mechanics: {analysis['mechanics']}")
        print(f"  Is DoT: {analysis['is_dot']}, Is Hit: {analysis['is_hit']}")

        # 추천 스탯 확인
        recommended_stats = analyzer.get_recommended_stats(analysis)
        print(f"  Recommended Stats: {', '.join(recommended_stats[:5])}")

    print("\n✅ Mechanics Analyzer test completed\n")


def test_context_builder_integration():
    """Context Builder 통합 테스트"""
    print("=" * 60)
    print("TEST 2: Context Builder Integration")
    print("=" * 60)

    # DB 연결
    db_path = project_root / "data" / "torchlight.db"
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return

    engine = create_engine(f"sqlite:///{db_path}")
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Context Builder 생성
        context_builder = ContextBuilder(db)
        print("✅ Context Builder initialized with MechanicsAnalyzer\n")

        # 첫 번째 영웅으로 컨텍스트 생성
        hero_id = 1
        print(f"📋 Building context for hero_id={hero_id}...")

        context = context_builder.build_hero_context(
            hero_id=hero_id,
            playstyle="DoT",
            max_skills=10,
            max_items=10
        )

        # 컨텍스트 확인
        print(f"\n✅ Context built successfully!")
        print(f"  Hero: {context['hero']['name']}")
        print(f"  Talent: {context['hero']['talent']}")
        print(f"  Skills: {len(context['available_skills'])} skills")
        print(f"  Items: {len(context['available_items'])} items")

        # 스킬 메커니즘 분석 결과 확인
        print("\n📊 Skill Mechanics Analysis:")
        for i, skill in enumerate(context['available_skills'][:5], 1):
            print(f"\n  {i}. {skill['name']}")
            print(f"     Build Style: {skill.get('build_style', 'N/A')}")
            print(f"     Ailment: {skill.get('ailment', 'N/A')}")
            print(f"     Mechanics: {skill.get('mechanics', [])}")

        # 빌드 제안 생성
        print("\n📊 Build Suggestions:")
        suggestions = context_builder.get_build_suggestions(context)
        print(f"  Build Type: {suggestions['build_type']}")
        print(f"  Dominant Damage: {suggestions['dominant_damage']}")
        print(f"  Recommended Stats: {', '.join(suggestions['recommended_stats'][:5])}")
        print(f"  Playstyle Tips:")
        for tip in suggestions['playstyle_tips']:
            print(f"    • {tip}")

        # 프롬프트 포맷팅 확인
        print("\n📝 Formatted Prompt Preview:")
        prompt = context_builder.format_context_for_prompt(context)
        prompt_lines = prompt.split('\n')
        print('\n'.join(prompt_lines[:50]))  # 첫 50줄만
        print(f"\n... (Total {len(prompt_lines)} lines)")

        print("\n✅ Context Builder integration test completed")

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def test_synergy_calculation():
    """시너지 계산 테스트"""
    print("\n" + "=" * 60)
    print("TEST 3: Synergy Calculation")
    print("=" * 60)

    analyzer = MechanicsAnalyzer()

    # DoT 빌드 시너지 테스트
    dot_skill_analyses = [
        {
            "build_style": "DoT",
            "damage_type": "Fire",
            "ailment": "Ignite",
            "mechanics": {"AoE"}
        },
        {
            "build_style": "DoT",
            "damage_type": "Fire",
            "ailment": "Ignite",
            "mechanics": set()
        }
    ]

    # 좋은 시너지 아이템 (DoT용)
    good_item_effects = [
        "Increases Affliction by 50%",
        "Adds 30% more Fire Damage",
        "Grants Reaping effect"
    ]

    score, reasons = analyzer.calculate_synergy_score(dot_skill_analyses, good_item_effects)
    print(f"\n🔥 DoT Build + DoT Items:")
    print(f"  Synergy Score: {score}/100")
    print(f"  Reasons:")
    for reason in reasons:
        print(f"    {reason}")

    # 나쁜 시너지 (DoT 빌드에 Crit 아이템)
    bad_item_effects = [
        "Increases Critical Strike Chance by 20%",
        "Adds 50% Critical Strike Damage"
    ]

    score, reasons = analyzer.calculate_synergy_score(dot_skill_analyses, bad_item_effects)
    print(f"\n⚠️  DoT Build + Crit Items (Mismatch):")
    print(f"  Synergy Score: {score}/100")
    print(f"  Reasons:")
    for reason in reasons:
        print(f"    {reason}")

    print("\n✅ Synergy calculation test completed")


if __name__ == "__main__":
    print("\n🚀 Starting Mechanics-Aware Recommendation System Tests\n")

    try:
        test_mechanics_analyzer()
        test_context_builder_integration()
        test_synergy_calculation()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
