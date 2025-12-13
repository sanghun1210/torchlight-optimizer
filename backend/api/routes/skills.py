"""
스킬(Skills) API 라우터
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.db import get_db_session
from backend.database.models import Skill
from backend.schemas.schemas import SkillResponse

router = APIRouter()


@router.get("/", response_model=List[SkillResponse])
def get_skills(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(100, ge=1, le=500, description="가져올 항목 수"),
    skill_type: Optional[str] = Query(None, description="스킬 타입 필터 (Active, Support, etc.)"),
    damage_type: Optional[str] = Query(None, description="데미지 타입 필터 (Physical, Fire, etc.)"),
    db: Session = Depends(get_db_session)
):
    """
    모든 스킬 목록 조회

    - **skip**: 건너뛸 항목 수
    - **limit**: 가져올 최대 항목 수
    - **skill_type**: 스킬 타입 필터 (Active, Support, Passive, etc.)
    - **damage_type**: 데미지 타입 필터 (Physical, Fire, Lightning, etc.)
    """
    query = db.query(Skill)

    # 스킬 타입 필터
    if skill_type:
        query = query.filter(Skill.type == skill_type)

    # 데미지 타입 필터
    if damage_type:
        query = query.filter(Skill.damage_type == damage_type)

    skills = query.offset(skip).limit(limit).all()
    return skills


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(
    skill_id: int,
    db: Session = Depends(get_db_session)
):
    """
    특정 스킬 상세 정보 조회

    - **skill_id**: 스킬 ID
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()

    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill with id {skill_id} not found")

    return skill


@router.get("/types/list")
def get_skill_types(db: Session = Depends(get_db_session)):
    """
    사용 가능한 모든 스킬 타입 목록 조회
    """
    skill_types = db.query(Skill.type).distinct().all()
    return {"skill_types": [st[0] for st in skill_types if st[0]]}


@router.get("/damage-types/list")
def get_damage_types(db: Session = Depends(get_db_session)):
    """
    사용 가능한 모든 데미지 타입 목록 조회
    """
    damage_types = db.query(Skill.damage_type).distinct().all()
    return {"damage_types": [dt[0] for dt in damage_types if dt[0]]}
