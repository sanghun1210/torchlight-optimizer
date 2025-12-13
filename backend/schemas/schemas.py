"""
Pydantic 스키마 정의 - API 요청/응답 모델
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# ============================================================================
# Hero Schemas
# ============================================================================

class HeroBase(BaseModel):
    """영웅 기본 스키마"""
    name: str
    god_type: str
    talent: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    popularity_score: Optional[float] = 0.0


class HeroResponse(HeroBase):
    """영웅 응답 스키마"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Skill Schemas
# ============================================================================

class SkillBase(BaseModel):
    """스킬 기본 스키마"""
    name: str
    type: str
    description: Optional[str] = None
    tags: Optional[str] = None  # JSON array string
    damage_type: Optional[str] = None
    cooldown: Optional[float] = None
    mana_cost: Optional[int] = None
    image_url: Optional[str] = None


class SkillResponse(SkillBase):
    """스킬 응답 스키마"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Item Schemas
# ============================================================================

class ItemBase(BaseModel):
    """아이템 기본 스키마"""
    name: str
    type: str
    slot: str
    rarity: Optional[str] = None
    stat_type: Optional[str] = None
    base_stats: Optional[str] = None  # JSON string
    special_effects: Optional[str] = None  # JSON string
    set_name: Optional[str] = None
    image_url: Optional[str] = None


class ItemResponse(ItemBase):
    """아이템 응답 스키마"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Talent Node Schemas
# ============================================================================

class TalentNodeBase(BaseModel):
    """재능 노드 기본 스키마"""
    name: str
    node_type: str  # Core, Regular
    god_class: Optional[str] = None
    tier: Optional[str] = None
    effect: Optional[str] = None
    image_url: Optional[str] = None


class TalentNodeResponse(TalentNodeBase):
    """재능 노드 응답 스키마"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Destiny Schemas
# ============================================================================

class DestinyBase(BaseModel):
    """운명 기본 스키마"""
    name: str
    tier: Optional[str] = None
    category: Optional[str] = None
    effect: Optional[str] = None
    stat_range: Optional[str] = None
    image_url: Optional[str] = None


class DestinyResponse(DestinyBase):
    """운명 응답 스키마"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Pagination Schema
# ============================================================================

class PaginatedResponse(BaseModel):
    """페이지네이션 응답 스키마"""
    total: int
    page: int
    page_size: int
    items: List[dict]


# ============================================================================
# Recommendation Schemas
# ============================================================================

class BuildRecommendationRequest(BaseModel):
    """빌드 추천 요청 스키마"""
    hero_id: int
    playstyle: Optional[str] = None  # Melee, Ranged, Tank, etc.
    focus: Optional[str] = None  # Damage, Defense, Utility


class SkillRecommendation(BaseModel):
    """추천 스킬"""
    skill_id: int
    skill_name: str
    reason: str
    priority: int


class ItemRecommendation(BaseModel):
    """추천 아이템"""
    item_id: int
    item_name: str
    slot: str
    reason: str


class BuildRecommendationResponse(BaseModel):
    """빌드 추천 응답 스키마"""
    hero_id: int
    hero_name: str
    recommended_skills: List[SkillRecommendation]
    recommended_items: List[ItemRecommendation]
    synergy_score: float
