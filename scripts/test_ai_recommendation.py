"""
AI 추천 시스템 테스트 스크립트

이 스크립트는 다음을 테스트합니다:
1. OpenAI API 키 설정 확인
2. Context Builder 동작 확인
3. AI Service 동작 확인
4. 전체 추천 파이프라인 테스트

사용법:
    python scripts/test_ai_recommendation.py
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.database.models import Base, Hero
from backend.recommendation.context_builder import ContextBuilder
from backend.recommendation.ai_service import AIRecommendationService


def test_environment_setup():
    """환경 변수 설정 확인"""
    print("=" * 60)
    print("1. 환경 변수 설정 확인")
    print("=" * 60)

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 OPENAI_API_KEY를 추가하세요.")
        return False

    print(f"✅ OPENAI_API_KEY 설정됨: {api_key[:10]}...{api_key[-4:]}")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    print(f"✅ 사용 모델: {model}")

    return True


def test_database_connection():
    """데이터베이스 연결 확인"""
    print("\n" + "=" * 60)
    print("2. 데이터베이스 연결 확인")
    print("=" * 60)

    try:
        db_path = project_root / "data" / "torchlight.db"
        if not db_path.exists():
            print(f"❌ 데이터베이스 파일이 없습니다: {db_path}")
            print("   scripts/init_database.py를 먼저 실행하세요.")
            return None

        engine = create_engine(f"sqlite:///{db_path}")
        session = Session(engine)

        # 영웅 데이터 확인
        hero_count = session.query(Hero).count()
        print(f"✅ 데이터베이스 연결 성공")
        print(f"✅ 영웅 데이터: {hero_count}개")

        if hero_count == 0:
            print("⚠️  영웅 데이터가 없습니다. scripts/crawl_all_data.py를 실행하세요.")

        return session

    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return None


def test_context_builder(db: Session):
    """Context Builder 테스트"""
    print("\n" + "=" * 60)
    print("3. Context Builder 테스트")
    print("=" * 60)

    try:
        # 첫 번째 영웅으로 테스트
        first_hero = db.query(Hero).first()
        if not first_hero:
            print("❌ 영웅 데이터가 없습니다.")
            return None

        print(f"테스트 영웅: {first_hero.name} ({first_hero.talent})")

        context_builder = ContextBuilder(db)
        context = context_builder.build_hero_context(
            hero_id=first_hero.id,
            playstyle="Melee",
            max_skills=10,
            max_items=10
        )

        print(f"✅ Context 생성 성공")
        print(f"   - 영웅: {context['hero']['name']}")
        print(f"   - 재능 메커니즘: {len(context['talent_mechanics'])}개")
        print(f"   - 스킬: {len(context['available_skills'])}개")
        print(f"   - 아이템: {len(context['available_items'])}개")

        # 프롬프트 생성 테스트
        prompt_text = context_builder.format_context_for_prompt(context)
        print(f"✅ 프롬프트 생성 성공 ({len(prompt_text)} 글자)")

        return context

    except Exception as e:
        print(f"❌ Context Builder 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_ai_service(context: dict):
    """AI Service 테스트"""
    print("\n" + "=" * 60)
    print("4. AI Service 테스트")
    print("=" * 60)

    try:
        ai_service = AIRecommendationService()
        print(f"✅ AI Service 초기화 성공")
        print(f"   모델: {ai_service.model}")

        print("\n⏳ AI 추천 생성 중... (30초 정도 소요)")
        recommendation = ai_service.generate_build_recommendation(
            context=context,
            max_skills=4,
            max_items=6
        )

        print(f"\n✅ AI 추천 생성 성공!")
        print(f"\n{'=' * 60}")
        print(f"추천 결과:")
        print(f"{'=' * 60}")
        print(f"영웅: {recommendation.get('hero_name')}")
        print(f"재능: {recommendation.get('talent_name')}")
        print(f"빌드 타입: {recommendation.get('build_type')}")
        print(f"\n빌드 요약:")
        print(f"{recommendation.get('build_summary')}")

        print(f"\n추천 스킬:")
        for skill in recommendation.get('recommended_skills', [])[:3]:
            print(f"  - {skill.get('skill_name')}: {skill.get('reason')}")

        print(f"\n추천 아이템:")
        for item in recommendation.get('recommended_items', [])[:3]:
            print(f"  - {item.get('item_name')} ({item.get('slot')})")

        print(f"\n토큰 사용량:")
        metadata = recommendation.get('ai_metadata', {})
        print(f"  - 프롬프트: {metadata.get('prompt_tokens')} 토큰")
        print(f"  - 응답: {metadata.get('completion_tokens')} 토큰")
        print(f"  - 총: {metadata.get('tokens_used')} 토큰")

        return True

    except Exception as e:
        print(f"❌ AI Service 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 테스트 실행"""
    print("\n🧪 AI 추천 시스템 테스트 시작\n")

    # 1. 환경 변수 확인
    if not test_environment_setup():
        print("\n❌ 환경 설정 실패. .env 파일을 확인하세요.")
        return

    # 2. DB 연결 확인
    db = test_database_connection()
    if not db:
        print("\n❌ 데이터베이스 연결 실패.")
        return

    # 3. Context Builder 테스트
    context = test_context_builder(db)
    if not context:
        print("\n❌ Context Builder 실패.")
        return

    # 4. AI Service 테스트
    success = test_ai_service(context)

    if success:
        print("\n" + "=" * 60)
        print("✅ 모든 테스트 통과!")
        print("=" * 60)
        print("\n다음 단계:")
        print("  1. FastAPI 서버 실행: uvicorn backend.main:app --reload")
        print("  2. API 테스트: http://localhost:8000/docs")
        print("  3. AI 엔드포인트: GET /api/recommendations/ai/build/1")
    else:
        print("\n❌ AI Service 테스트 실패.")

    db.close()


if __name__ == "__main__":
    main()
