"""
영웅(Heroes) API 라우터
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.db import get_db_session
from backend.database.models import Hero
from backend.schemas.schemas import HeroResponse

router = APIRouter()


@router.get("/", response_model=List[HeroResponse])
def get_heroes(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(100, ge=1, le=500, description="가져올 항목 수"),
    god_type: Optional[str] = Query(None, description="God 타입 필터"),
    db: Session = Depends(get_db_session)
):
    """
    모든 영웅 목록 조회

    - **skip**: 건너뛸 항목 수 (페이지네이션)
    - **limit**: 가져올 최대 항목 수
    - **god_type**: God 타입으로 필터링 (예: "God of Might")
    """
    query = db.query(Hero)

    # God 타입 필터
    if god_type:
        query = query.filter(Hero.god_type == god_type)

    heroes = query.offset(skip).limit(limit).all()
    return heroes


@router.get("/{hero_id}", response_model=HeroResponse)
def get_hero(
    hero_id: int,
    db: Session = Depends(get_db_session)
):
    """
    특정 영웅 상세 정보 조회

    - **hero_id**: 영웅 ID
    """
    hero = db.query(Hero).filter(Hero.id == hero_id).first()

    if not hero:
        raise HTTPException(status_code=404, detail=f"Hero with id {hero_id} not found")

    return hero


@router.get("/talent/{talent_name}", response_model=HeroResponse)
def get_hero_by_talent(
    talent_name: str,
    db: Session = Depends(get_db_session)
):
    """
    재능(Talent) 이름으로 영웅 조회

    - **talent_name**: 재능 이름
    """
    hero = db.query(Hero).filter(Hero.talent == talent_name).first()

    if not hero:
        raise HTTPException(status_code=404, detail=f"Hero with talent '{talent_name}' not found")

    return hero


@router.get("/god-types/list")
def get_god_types(db: Session = Depends(get_db_session)):
    """
    사용 가능한 모든 God 타입 목록 조회
    """
    god_types = db.query(Hero.god_type).distinct().all()
    return {"god_types": [gt[0] for gt in god_types]}
