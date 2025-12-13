"""
재능 노드(Talent Nodes) API 라우터
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.db import get_db_session
from backend.database.models import TalentNode
from backend.schemas.schemas import TalentNodeResponse

router = APIRouter()


@router.get("/", response_model=List[TalentNodeResponse])
def get_talent_nodes(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(200, ge=1, le=500, description="가져올 항목 수"),
    node_type: Optional[str] = Query(None, description="노드 타입 필터 (Core, Regular)"),
    god_class: Optional[str] = Query(None, description="God 클래스 필터"),
    tier: Optional[str] = Query(None, description="티어 필터 (Micro, Medium, Large)"),
    db: Session = Depends(get_db_session)
):
    """
    모든 재능 노드 목록 조회

    - **skip**: 건너뛸 항목 수
    - **limit**: 가져올 최대 항목 수
    - **node_type**: 노드 타입 (Core, Regular)
    - **god_class**: God 클래스 필터
    - **tier**: 티어 필터 (Micro, Medium, Large)
    """
    query = db.query(TalentNode)

    # 필터
    if node_type:
        query = query.filter(TalentNode.node_type == node_type)
    if god_class:
        query = query.filter(TalentNode.god_class == god_class)
    if tier:
        query = query.filter(TalentNode.tier.like(f"%{tier}%"))

    nodes = query.offset(skip).limit(limit).all()
    return nodes


@router.get("/{node_id}", response_model=TalentNodeResponse)
def get_talent_node(
    node_id: int,
    db: Session = Depends(get_db_session)
):
    """
    특정 재능 노드 상세 정보 조회

    - **node_id**: 재능 노드 ID
    """
    node = db.query(TalentNode).filter(TalentNode.id == node_id).first()

    if not node:
        raise HTTPException(status_code=404, detail=f"Talent node with id {node_id} not found")

    return node


@router.get("/types/list")
def get_node_types(db: Session = Depends(get_db_session)):
    """
    사용 가능한 모든 노드 타입 목록 조회
    """
    node_types = db.query(TalentNode.node_type).distinct().all()
    return {"node_types": [nt[0] for nt in node_types if nt[0]]}


@router.get("/god-classes/list")
def get_god_classes(db: Session = Depends(get_db_session)):
    """
    사용 가능한 모든 God 클래스 목록 조회
    """
    god_classes = db.query(TalentNode.god_class).distinct().all()
    return {"god_classes": [gc[0] for gc in god_classes if gc[0]]}
