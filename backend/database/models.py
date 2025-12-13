"""
SQLAlchemy 데이터베이스 모델 정의
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class Hero(Base):
    """영웅(Heroes) 테이블"""
    __tablename__ = "heroes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # 영웅 이름 (중복 가능, 여러 talent 보유)
    god_type = Column(String(50), nullable=False)  # God of Might, Wisdom, etc.
    talent = Column(String(50), nullable=False, unique=True)  # Talent는 고유해야 함
    description = Column(Text)
    image_url = Column(String(500))
    popularity_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hero_skills = relationship("HeroSkill", back_populates="hero", cascade="all, delete-orphan")
    meta_builds = relationship("MetaBuild", back_populates="hero", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Hero(id={self.id}, name='{self.name}', god_type='{self.god_type}')>"


class Skill(Base):
    """스킬(Skills) 테이블"""
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # Active, Support, Passive, etc.
    description = Column(Text)
    tags = Column(Text)  # JSON array: ["AoE", "DoT", "Melee"]
    damage_type = Column(String(50))  # Physical, Fire, Lightning, etc.
    cooldown = Column(Float)
    mana_cost = Column(Integer)
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hero_skills = relationship("HeroSkill", back_populates="skill", cascade="all, delete-orphan")
    synergies_a = relationship(
        "SkillSynergy",
        foreign_keys="SkillSynergy.skill_a_id",
        back_populates="skill_a",
        cascade="all, delete-orphan"
    )
    synergies_b = relationship(
        "SkillSynergy",
        foreign_keys="SkillSynergy.skill_b_id",
        back_populates="skill_b",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Skill(id={self.id}, name='{self.name}', type='{self.type}')>"


class Item(Base):
    """아이템(Items) 테이블"""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # Helmet, Armor, Weapon, etc.
    slot = Column(String(50), nullable=False)  # Head, Chest, MainHand, etc.
    rarity = Column(String(50))  # Common, Rare, Legendary, etc.
    stat_type = Column(String(20))  # STR, DEX, INT
    base_stats = Column(Text)  # JSON: {"armor": 100, "health": 50}
    special_effects = Column(Text)  # JSON array
    set_name = Column(String(100))  # 세트 아이템인 경우
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}', type='{self.type}')>"


class HeroSkill(Base):
    """영웅-스킬 연관(Hero_Skills) 테이블"""
    __tablename__ = "hero_skills"
    __table_args__ = (
        UniqueConstraint('hero_id', 'skill_id', name='uq_hero_skill'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    hero_id = Column(Integer, ForeignKey('heroes.id'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills.id'), nullable=False)
    recommended_level = Column(Integer)  # 추천 레벨
    priority = Column(Integer)  # 우선순위 (1=최우선)

    # Relationships
    hero = relationship("Hero", back_populates="hero_skills")
    skill = relationship("Skill", back_populates="hero_skills")

    def __repr__(self):
        return f"<HeroSkill(hero_id={self.hero_id}, skill_id={self.skill_id}, priority={self.priority})>"


class SkillSynergy(Base):
    """스킬 시너지(Skill_Synergies) 테이블"""
    __tablename__ = "skill_synergies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_a_id = Column(Integer, ForeignKey('skills.id'), nullable=False)
    skill_b_id = Column(Integer, ForeignKey('skills.id'), nullable=False)
    synergy_score = Column(Float, nullable=False)  # 0.0 ~ 1.0
    synergy_type = Column(String(50))  # damage_boost, cooldown_reduction, etc.
    description = Column(Text)

    # Relationships
    skill_a = relationship("Skill", foreign_keys=[skill_a_id], back_populates="synergies_a")
    skill_b = relationship("Skill", foreign_keys=[skill_b_id], back_populates="synergies_b")

    def __repr__(self):
        return f"<SkillSynergy(skill_a={self.skill_a_id}, skill_b={self.skill_b_id}, score={self.synergy_score})>"


class ItemSet(Base):
    """아이템 세트(Item_Sets) 테이블"""
    __tablename__ = "item_sets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    set_name = Column(String(100), nullable=False, unique=True)
    pieces_required = Column(Integer, nullable=False)
    set_bonus_2 = Column(Text)  # 2피스 효과
    set_bonus_4 = Column(Text)  # 4피스 효과
    set_bonus_6 = Column(Text)  # 6피스 효과
    description = Column(Text)

    def __repr__(self):
        return f"<ItemSet(id={self.id}, name='{self.set_name}', pieces={self.pieces_required})>"


class TalentNode(Base):
    """재능 노드(Talent_Nodes) 테이블"""
    __tablename__ = "talent_nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    node_type = Column(String(20), nullable=False)  # Core, Regular
    god_class = Column(String(50))  # New God, God of Might, etc.
    tier = Column(String(20))  # Micro, Medium, Large (for regular nodes)
    effect = Column(Text)  # 효과 설명
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TalentNode(id={self.id}, name='{self.name}', type='{self.node_type}')>"


class TalentLevel(Base):
    """재능 레벨 효과(Talent_Levels) 테이블"""
    __tablename__ = "talent_levels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    talent_name = Column(String(100), nullable=False)  # "Anger", "Seething Silhouette" 등
    level = Column(Integer, nullable=False)  # 1, 45, 60, 75 등
    effect_name = Column(String(100), nullable=False)  # "Tunnel Vision", "Rampaging" 등
    effect_description = Column(Text)  # 효과 상세 설명
    mechanics = Column(Text)  # JSON: 핵심 메커니즘 키워드
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TalentLevel(talent='{self.talent_name}', level={self.level}, effect='{self.effect_name}')>"


class Destiny(Base):
    """운명(Destiny/Fate) 테이블"""
    __tablename__ = "destinies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    tier = Column(String(20))  # Micro, Medium, Large
    category = Column(String(50))  # Fire Resistance, Attack Damage, etc.
    effect = Column(Text)  # 효과 설명
    stat_range = Column(String(50))  # (5-7), (14-18), etc.
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Destiny(id={self.id}, name='{self.name}', tier='{self.tier}')>"


class MetaBuild(Base):
    """메타 빌드(Meta_Builds) 테이블"""
    __tablename__ = "meta_builds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hero_id = Column(Integer, ForeignKey('heroes.id'), nullable=False)
    build_name = Column(String(100), nullable=False)
    season = Column(String(20))  # S1, S2, etc.
    popularity_rank = Column(Integer)
    skill_combination = Column(Text)  # JSON array of skill IDs
    item_recommendation = Column(Text)  # JSON array of item IDs
    playstyle = Column(String(50))  # Melee, Ranged, Tank, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hero = relationship("Hero", back_populates="meta_builds")

    def __repr__(self):
        return f"<MetaBuild(id={self.id}, hero_id={self.hero_id}, name='{self.build_name}')>"
