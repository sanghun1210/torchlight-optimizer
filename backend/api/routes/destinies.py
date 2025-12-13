"""
운명(Destinies) API 라우터
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.db import get_db_session
from backend.database.models import Destiny
from backend.schemas.schemas import DestinyResponse

router = APIRouter()


@router.get("/", response_model=List[DestinyResponse])
def get_destinies(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(200, ge=1, le=500, description="가져올 항목 수"),
    tier: Optional[str] = Query(None, description="티어 필터 (Micro, Medium, Large)"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    db: Session = Depends(get_db_session)
):
    """
    모든 운명 목록 조회

    - **skip**: 건너뛸 항목 수
    - **limit**: 가져올 최대 항목 수
    - **tier**: 티어 필터 (Micro, Medium, Large)
    - **category**: 카테고리 필터 (Fire Resistance, Attack Damage, etc.)
    """
    query = db.query(Destiny)

    # 필터
    if tier:
        query = query.filter(Destiny.tier == tier)
    if category:
        query = query.filter(Destiny.category.like(f"%{category}%"))

    destinies = query.offset(skip).limit(limit).all()
    return destinies


@router.get("/{destiny_id}", response_model=DestinyResponse)
def get_destiny(
    destiny_id: int,
    db: Session = Depends(get_db_session)
):
    """
    특정 운명 상세 정보 조회

    - **destiny_id**: 운명 ID
    """
    destiny = db.query(Destiny).filter(Destiny.id == destiny_id).first()

    if not destiny:
        raise HTTPException(status_code=404, detail=f"Destiny with id {destiny_id} not found")

    return destiny


@router.get("/tiers/list")
def get_destiny_tiers(db: Session = Depends(get_db_session)):
    """
    사용 가능한 모든 운명 티어 목록 조회
    """
    tiers = db.query(Destiny.tier).distinct().all()
    return {"tiers": [t[0] for t in tiers if t[0]]}


@router.get("/categories/list")
def get_destiny_categories(db: Session = Depends(get_db_session)):
    """
    사용 가능한 모든 운명 카테고리 목록 조회
    """
    categories = db.query(Destiny.category).distinct().all()
    return {"categories": [c[0] for c in categories if c[0]]}
