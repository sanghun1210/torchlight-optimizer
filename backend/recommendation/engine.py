"""
빌드 추천 엔진
"""
import json
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from collections import Counter

from backend.database.models import Hero, Skill, Item, TalentNode


class RecommendationEngine:
    """빌드 추천 엔진"""

    # God Type과 Stat Type 매핑
    GOD_TO_STAT = {
        "Berserker": "STR",
        "Warrior": "STR",
        "Commander": "STR",
        "Ranger": "DEX",
        "Spacetime Witness": "DEX",
        "Carino": "DEX",
        "Mage": "INT",
        "Oracle": "INT",
        "Divineshot": "DEX",
    }

    def __init__(self, db: Session):
        self.db = db

    def recommend_build(
        self,
        hero_id: int,
        playstyle: Optional[str] = None,
        focus: Optional[str] = None,
        max_skills: int = 6,
        max_items: int = 10
    ) -> Dict:
        """
        영웅 기반 빌드 추천

        Args:
            hero_id: 영웅 ID
            playstyle: 플레이스타일 (Melee, Ranged, Tank 등)
            focus: 빌드 초점 (Damage, Defense, Utility 등)
            max_skills: 추천할 최대 스킬 개수
            max_items: 추천할 최대 아이템 개수

        Returns:
            추천 빌드 딕셔너리
        """
        # 영웅 정보 가져오기
        hero = self.db.query(Hero).filter(Hero.id == hero_id).first()
        if not hero:
            raise ValueError(f"Hero with id {hero_id} not found")

        # 스킬 추천
        recommended_skills = self._recommend_skills(hero, playstyle, max_skills)

        # 아이템 추천
        recommended_items = self._recommend_items(hero, recommended_skills, max_items)

        # 재능 노드 추천
        recommended_talents = self._recommend_talent_nodes(hero, max_nodes=5)

        # 시너지 점수 계산
        synergy_score = self._calculate_synergy_score(
            recommended_skills,
            recommended_items
        )

        return {
            "hero_id": hero.id,
            "hero_name": hero.name,
            "hero_talent": hero.talent,
            "god_type": hero.god_type,
            "recommended_skills": recommended_skills,
            "recommended_items": recommended_items,
            "recommended_talents": recommended_talents,
            "synergy_score": round(synergy_score, 2),
            "build_summary": self._generate_build_summary(
                hero, recommended_skills, recommended_items
            )
        }

    def _recommend_skills(
        self,
        hero: Hero,
        playstyle: Optional[str],
        max_skills: int
    ) -> List[Dict]:
        """스킬 추천"""
        all_skills = self.db.query(Skill).all()
        scored_skills = []

        for skill in all_skills:
            score = 0
            reasons = []

            # 1. 스킬 타입 점수
            if skill.type == "Active Skill":
                score += 10
                reasons.append("핵심 액티브 스킬")
            elif skill.type == "Support Skill":
                score += 5
                reasons.append("서포트 스킬")

            # 2. 데미지 타입 일관성 (같은 damage_type 선호)
            if skill.damage_type:
                score += 3
                reasons.append(f"{skill.damage_type} 데미지")

            # 3. 태그 분석
            if skill.tags:
                try:
                    tags = json.loads(skill.tags)

                    # AoE 스킬 보너스
                    if "AoE" in tags:
                        score += 2
                        reasons.append("광역 공격")

                    # Melee/Ranged 플레이스타일 매칭
                    if playstyle:
                        if playstyle.lower() in [tag.lower() for tag in tags]:
                            score += 5
                            reasons.append(f"{playstyle} 스타일 매칭")

                except json.JSONDecodeError:
                    pass

            # 4. 설명이 풍부한 스킬 우선
            if skill.description and len(skill.description) > 50:
                score += 1

            scored_skills.append({
                "skill_id": skill.id,
                "skill_name": skill.name,
                "skill_type": skill.type,
                "damage_type": skill.damage_type,
                "tags": skill.tags,
                "score": score,
                "reason": ", ".join(reasons) if reasons else "기본 추천",
                "priority": 1  # 나중에 우선순위 조정 가능
            })

        # 점수순 정렬
        scored_skills.sort(key=lambda x: x["score"], reverse=True)

        # 상위 N개 반환
        return scored_skills[:max_skills]

    def _recommend_items(
        self,
        hero: Hero,
        recommended_skills: List[Dict],
        max_items: int
    ) -> List[Dict]:
        """아이템 추천"""
        # God Type에 맞는 Stat Type 결정
        preferred_stat = self.GOD_TO_STAT.get(hero.god_type, "STR")

        # 스킬들의 데미지 타입 분석
        damage_types = [
            skill.get("damage_type")
            for skill in recommended_skills
            if skill.get("damage_type")
        ]
        primary_damage = Counter(damage_types).most_common(1)
        primary_damage_type = primary_damage[0][0] if primary_damage else None

        all_items = self.db.query(Item).all()
        scored_items = []

        for item in all_items:
            score = 0
            reasons = []

            # 1. Stat Type 매칭
            if item.stat_type == preferred_stat:
                score += 10
                reasons.append(f"{preferred_stat} 스탯 매칭")

            # 2. 레전더리 아이템 우선
            if item.rarity == "Legendary":
                score += 5
                reasons.append("레전더리")

            # 3. 세트 아이템 보너스
            if item.set_name:
                score += 3
                reasons.append(f"{item.set_name} 세트")

            # 4. 데미지 타입 매칭 (special_effects에서)
            if primary_damage_type and item.special_effects:
                if primary_damage_type.lower() in item.special_effects.lower():
                    score += 5
                    reasons.append(f"{primary_damage_type} 시너지")

            scored_items.append({
                "item_id": item.id,
                "item_name": item.name,
                "slot": item.slot,
                "type": item.type,
                "rarity": item.rarity,
                "set_name": item.set_name,
                "score": score,
                "reason": ", ".join(reasons) if reasons else "기본 추천"
            })

        # 점수순 정렬
        scored_items.sort(key=lambda x: x["score"], reverse=True)

        # 슬롯별로 균형있게 선택 (각 슬롯당 최대 1개)
        selected_items = []
        used_slots = set()

        for item in scored_items:
            slot = item["slot"]
            if slot not in used_slots:
                selected_items.append(item)
                used_slots.add(slot)

            if len(selected_items) >= max_items:
                break

        return selected_items

    def _recommend_talent_nodes(
        self,
        hero: Hero,
        max_nodes: int = 5
    ) -> List[Dict]:
        """재능 노드 추천"""
        all_nodes = self.db.query(TalentNode).all()
        scored_nodes = []

        for node in all_nodes:
            score = 0
            reasons = []

            # 1. Core 노드 우선
            if node.node_type == "Core":
                score += 10
                reasons.append("코어 노드")
            else:
                score += 3

            # 2. God Class 매칭
            if node.god_class and hero.god_type:
                if hero.god_type.lower() in node.god_class.lower():
                    score += 8
                    reasons.append(f"{hero.god_type} 매칭")

            # 3. Tier 점수 (Large > Medium > Micro)
            if node.tier:
                if "Large" in node.tier or "Legendary" in node.tier:
                    score += 5
                    reasons.append("대형 노드")
                elif "Medium" in node.tier:
                    score += 3
                    reasons.append("중형 노드")

            scored_nodes.append({
                "node_id": node.id,
                "node_name": node.name,
                "node_type": node.node_type,
                "tier": node.tier,
                "god_class": node.god_class,
                "score": score,
                "reason": ", ".join(reasons) if reasons else "기본 추천"
            })

        # 점수순 정렬
        scored_nodes.sort(key=lambda x: x["score"], reverse=True)

        return scored_nodes[:max_nodes]

    def _calculate_synergy_score(
        self,
        skills: List[Dict],
        items: List[Dict]
    ) -> float:
        """시너지 점수 계산"""
        synergy = 0.0

        # 스킬 간 데미지 타입 일관성
        damage_types = [s.get("damage_type") for s in skills if s.get("damage_type")]
        if damage_types:
            most_common = Counter(damage_types).most_common(1)[0]
            consistency_ratio = most_common[1] / len(damage_types)
            synergy += consistency_ratio * 30  # 최대 30점

        # 스킬 개수 보너스
        synergy += min(len(skills) * 5, 30)  # 최대 30점

        # 아이템 개수 보너스
        synergy += min(len(items) * 3, 30)  # 최대 30점

        # 세트 아이템 보너스
        set_items = [i for i in items if i.get("set_name")]
        synergy += len(set_items) * 2  # 세트 아이템당 2점

        return min(synergy, 100.0)  # 최대 100점

    def _generate_build_summary(
        self,
        hero: Hero,
        skills: List[Dict],
        items: List[Dict]
    ) -> str:
        """빌드 요약 생성"""
        damage_types = [s.get("damage_type") for s in skills if s.get("damage_type")]
        primary_damage = Counter(damage_types).most_common(1)

        if primary_damage:
            damage_focus = primary_damage[0][0]
        else:
            damage_focus = "혼합"

        set_items = [i.get("set_name") for i in items if i.get("set_name")]
        unique_sets = set(set_items)

        summary = f"{hero.name} ({hero.talent}) 빌드 - {damage_focus} 데미지 중심"

        if unique_sets:
            summary += f", {len(unique_sets)}개 세트 아이템 활용"

        return summary
