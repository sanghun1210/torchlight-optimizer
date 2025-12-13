"""
빌드 추천 API 라우터 (v2 엔진 + AI 엔진)
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.db import get_db_session
from backend.recommendation.engine_v2 import RecommendationEngineV2
from backend.recommendation.context_builder import ContextBuilder
from backend.recommendation.ai_service import AIRecommendationService

router = APIRouter()


@router.get("/build/{hero_id}")
def get_build_recommendation(
    hero_id: int,
    playstyle: Optional[str] = Query(None, description="플레이스타일 (Melee, Ranged, etc.)"),
    focus: Optional[str] = Query(None, description="빌드 초점 (Damage, Defense, Utility)"),
    max_skills: int = Query(6, ge=1, le=10, description="추천할 스킬 개수"),
    max_items: int = Query(10, ge=1, le=20, description="추천할 아이템 개수"),
    db: Session = Depends(get_db_session)
):
    """
    영웅 기반 빌드 추천

    - **hero_id**: 영웅 ID
    - **playstyle**: 플레이스타일 (선택사항)
    - **focus**: 빌드 초점 (선택사항)
    - **max_skills**: 추천할 최대 스킬 개수
    - **max_items**: 추천할 최대 아이템 개수
    """
    try:
        engine = RecommendationEngineV2(db)
        recommendation = engine.recommend_build(
            hero_id=hero_id,
            playstyle=playstyle,
            focus=focus,
            max_skills=max_skills,
            max_items=max_items
        )
        return recommendation

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@router.get("/quick/{hero_id}")
def get_quick_recommendation(
    hero_id: int,
    db: Session = Depends(get_db_session)
):
    """
    빠른 빌드 추천 (기본 설정)

    - **hero_id**: 영웅 ID
    """
    try:
        engine = RecommendationEngineV2(db)
        recommendation = engine.recommend_build(
            hero_id=hero_id,
            max_skills=4,
            max_items=6
        )
        return {
            "hero_name": recommendation["hero_name"],
            "talent": recommendation["hero_talent"],
            "build_type": recommendation["build_type"],
            "primary_stat": recommendation["primary_stat"],
            "build_summary": recommendation["build_summary"],
            "synergy_score": recommendation["synergy_score"],
            "top_skills": [
                {
                    "name": s["skill_name"],
                    "type": s["skill_type"],
                    "damage_type": s.get("damage_type"),
                    "is_dot": s.get("is_dot"),
                    "reason": s["reason"]
                }
                for s in recommendation["recommended_skills"][:3]
            ],
            "top_items": [
                {
                    "name": i["item_name"],
                    "slot": i["slot"],
                    "reason": i["reason"]
                }
                for i in recommendation["recommended_items"][:3]
            ]
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@router.get("/ai/build/{hero_id}")
def get_ai_build_recommendation(
    hero_id: int,
    playstyle: Optional[str] = Query(None, description="플레이스타일 (Melee, Ranged, Fire, DoT 등)"),
    max_skills: int = Query(6, ge=1, le=10, description="추천할 스킬 개수"),
    max_items: int = Query(10, ge=1, le=20, description="추천할 아이템 개수"),
    db: Session = Depends(get_db_session)
):
    """
    AI 기반 빌드 추천 (OpenAI API)

    - **hero_id**: 영웅 ID
    - **playstyle**: 플레이스타일 (선택사항)
    - **max_skills**: 추천할 최대 스킬 개수
    - **max_items**: 추천할 최대 아이템 개수

    **새로운 AI 기반 추천 시스템**:
    - 로컬 DB 데이터를 기반으로 컨텍스트 생성
    - OpenAI API를 통해 시너지 분석
    - 데이터 무결성 보장 (환각 방지)
    """
    try:
        # 1. Context Builder로 DB 데이터 수집
        context_builder = ContextBuilder(db)
        context = context_builder.build_hero_context(
            hero_id=hero_id,
            playstyle=playstyle,
            max_skills=50,  # 충분한 옵션 제공
            max_items=50
        )

        # 2. AI 서비스로 추천 생성
        ai_service = AIRecommendationService()
        recommendation = ai_service.generate_build_recommendation(
            context=context,
            max_skills=max_skills,
            max_items=max_items
        )

        # 3. 메타데이터 추가
        recommendation["source"] = "ai"
        recommendation["hero_id"] = hero_id

        return recommendation

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI recommendation failed: {str(e)}")


@router.get("/ai/quick/{hero_id}")
async def get_quick_ai_recommendation(
    hero_id: int,
    db: Session = Depends(get_db_session)
):
    """
    빠른 AI 빌드 추천 (기본 설정)

    - **hero_id**: 영웅 ID

    기본 설정으로 빠르게 빌드 추천을 받습니다.
    """
    try:
        # Context 생성
        context_builder = ContextBuilder(db)
        context = context_builder.build_hero_context(
            hero_id=hero_id,
            max_skills=30,  # 빠른 추천용
            max_items=30
        )

        # AI 추천
        ai_service = AIRecommendationService()
        recommendation = await ai_service.generate_build_recommendation_async(
            context=context,
            max_skills=4,
            max_items=6
        )

        # 간소화된 응답
        return {
            "hero_name": recommendation.get("hero_name"),
            "talent": recommendation.get("talent_name"),
            "build_type": recommendation.get("build_type"),
            "build_summary": recommendation.get("build_summary"),
            "recommended_skills": recommendation.get("recommended_skills", [])[:4],
            "recommended_items": recommendation.get("recommended_items", [])[:6],
            "synergy_explanation": recommendation.get("synergy_explanation"),
            "playstyle_tips": recommendation.get("playstyle_tips", []),
            "source": "ai",
            "tokens_used": recommendation.get("ai_metadata", {}).get("tokens_used")
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI quick recommendation failed: {str(e)}")
