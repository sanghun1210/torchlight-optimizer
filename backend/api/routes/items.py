"""
아이템(Items) API 라우터
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.db import get_db_session
from backend.database.models import Item
from backend.schemas.schemas import ItemResponse

router = APIRouter()


@router.get("/", response_model=List[ItemResponse])
def get_items(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(100, ge=1, le=500, description="가져올 항목 수"),
    item_type: Optional[str] = Query(None, description="아이템 타입 필터"),
    slot: Optional[str] = Query(None, description="장비 슬롯 필터"),
    rarity: Optional[str] = Query(None, description="희귀도 필터"),
    stat_type: Optional[str] = Query(None, description="스탯 타입 필터 (STR, DEX, INT)"),
    set_name: Optional[str] = Query(None, description="세트 이름 필터"),
    db: Session = Depends(get_db_session)
):
    """
    모든 아이템 목록 조회

    - **skip**: 건너뛸 항목 수
    - **limit**: 가져올 최대 항목 수
    - **item_type**: 아이템 타입 필터
    - **slot**: 장비 슬롯 필터 (Head, Chest, MainHand, etc.)
    - **rarity**: 희귀도 필터 (Legendary, etc.)
    - **stat_type**: 스탯 타입 필터 (STR, DEX, INT)
    - **set_name**: 세트 아이템 필터
    """
    query = db.query(Item)

    # 각종 필터
    if item_type:
        query = query.filter(Item.type == item_type)
    if slot:
        query = query.filter(Item.slot == slot)
    if rarity:
        query = query.filter(Item.rarity == rarity)
    if stat_type:
        query = query.filter(Item.stat_type == stat_type)
    if set_name:
        query = query.filter(Item.set_name == set_name)

    items = query.offset(skip).limit(limit).all()
    return items


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db_session)
):
    """
    특정 아이템 상세 정보 조회

    - **item_id**: 아이템 ID
    """
    item = db.query(Item).filter(Item.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")

    return item


@router.get("/types/list")
def get_item_types(db: Session = Depends(get_db_session)):
    """
    사용 가능한 모든 아이템 타입 목록 조회
    """
    item_types = db.query(Item.type).distinct().all()
    return {"item_types": [it[0] for it in item_types if it[0]]}


@router.get("/slots/list")
def get_slots(db: Session = Depends(get_db_session)):
    """
    사용 가능한 모든 장비 슬롯 목록 조회
    """
    slots = db.query(Item.slot).distinct().all()
    return {"slots": [s[0] for s in slots if s[0]]}


@router.get("/sets/list")
def get_set_names(db: Session = Depends(get_db_session)):
    """
    사용 가능한 모든 세트 이름 목록 조회
    """
    sets = db.query(Item.set_name).distinct().all()
    return {"set_names": [s[0] for s in sets if s[0]]}
