"""
빌드 추천 API 라우터 (v2 엔진 사용)
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.db import get_db_session
from backend.recommendation.engine_v2 import RecommendationEngineV2

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
