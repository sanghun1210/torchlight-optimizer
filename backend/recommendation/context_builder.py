"""
Context Builder - AI 프롬프트용 컨텍스트 생성
DB에서 관련 데이터를 쿼리하고 구조화된 프롬프트를 생성합니다.
"""
import json
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from backend.database.models import Hero, Skill, Item, TalentLevel, TalentNode


class ContextBuilder:
    """AI 추천을 위한 컨텍스트 빌더"""

    def __init__(self, db: Session):
        self.db = db

    def build_hero_context(
        self,
        hero_id: int,
        playstyle: Optional[str] = None,
        max_skills: int = 50,
        max_items: int = 50
    ) -> Dict:
        """
        영웅 기반 컨텍스트 생성

        Args:
            hero_id: 영웅 ID
            playstyle: 사용자 요청 플레이스타일 (선택사항)
            max_skills: 포함할 최대 스킬 개수
            max_items: 포함할 최대 아이템 개수

        Returns:
            구조화된 컨텍스트 딕셔너리
        """
        # 1. 영웅 정보 조회
        hero = self.db.query(Hero).filter(Hero.id == hero_id).first()
        if not hero:
            raise ValueError(f"Hero with id {hero_id} not found")

        # 2. 재능 레벨 효과 조회 (핵심 메커니즘)
        talent_levels = self._get_talent_levels(hero.talent)

        # 3. 관련 스킬 조회 (필터링)
        relevant_skills = self._get_relevant_skills(hero, playstyle, max_skills)

        # 4. 관련 아이템 조회 (필터링)
        relevant_items = self._get_relevant_items(hero, max_items)

        # 5. 컨텍스트 구조화
        context = {
            "hero": {
                "id": hero.id,
                "name": hero.name,
                "talent": hero.talent,
                "god_type": hero.god_type,
                "description": hero.description
            },
            "talent_mechanics": talent_levels,
            "available_skills": relevant_skills,
            "available_items": relevant_items,
            "user_preferences": {
                "playstyle": playstyle
            }
        }

        return context

    def _get_talent_levels(self, talent_name: str) -> List[Dict]:
        """재능의 모든 레벨 효과 조회"""
        talent_levels = self.db.query(TalentLevel).filter(
            TalentLevel.talent_name == talent_name
        ).order_by(TalentLevel.level).all()

        return [
            {
                "level": tl.level,
                "effect_name": tl.effect_name,
                "effect_description": tl.effect_description,
                "mechanics": json.loads(tl.mechanics) if tl.mechanics else []
            }
            for tl in talent_levels
        ]

    def _get_relevant_skills(
        self,
        hero: Hero,
        playstyle: Optional[str],
        max_skills: int
    ) -> List[Dict]:
        """관련 스킬 조회 및 필터링"""
        # 모든 스킬 조회 (실제로는 필터링 최적화 가능)
        skills = self.db.query(Skill).limit(max_skills).all()

        skill_list = []
        for skill in skills:
            # 태그 파싱
            tags = []
            if skill.tags:
                try:
                    tags = json.loads(skill.tags)
                except json.JSONDecodeError:
                    tags = []

            skill_data = {
                "id": skill.id,
                "name": skill.name,
                "type": skill.type,
                "description": skill.description[:200] if skill.description else "",  # 토큰 절약
                "tags": tags,
                "damage_type": skill.damage_type,
                "cooldown": skill.cooldown,
                "mana_cost": skill.mana_cost
            }

            # 플레이스타일 필터링 (선택사항)
            if playstyle:
                playstyle_lower = playstyle.lower()
                if any(playstyle_lower in tag.lower() for tag in tags):
                    skill_data["playstyle_match"] = True

            skill_list.append(skill_data)

        return skill_list

    def _get_relevant_items(self, hero: Hero, max_items: int) -> List[Dict]:
        """관련 아이템 조회 및 필터링"""
        # 영웅의 주 스탯과 매칭되는 아이템 우선
        primary_stat = self._get_primary_stat(hero.god_type)

        # 주 스탯 아이템 + 레전더리 아이템
        items = self.db.query(Item).filter(
            (Item.stat_type == primary_stat) | (Item.rarity == "Legendary")
        ).limit(max_items).all()

        item_list = []
        for item in items:
            # special_effects 파싱
            special_effects = []
            if item.special_effects:
                try:
                    special_effects = json.loads(item.special_effects)
                except json.JSONDecodeError:
                    # JSON이 아니면 문자열 그대로
                    special_effects = [item.special_effects[:100]]  # 토큰 절약

            item_list.append({
                "id": item.id,
                "name": item.name,
                "type": item.type,
                "slot": item.slot,
                "rarity": item.rarity,
                "stat_type": item.stat_type,
                "special_effects": special_effects,
                "set_name": item.set_name
            })

        return item_list

    def _get_primary_stat(self, god_type: str) -> str:
        """God Type에 따른 주 스탯 반환"""
        if "Might" in god_type or "Berserker" in god_type:
            return "STR"
        elif "Cunning" in god_type or "Ranger" in god_type:
            return "DEX"
        elif "Wisdom" in god_type or "Mage" in god_type:
            return "INT"
        else:
            return "STR"  # 기본값

    def format_context_for_prompt(self, context: Dict) -> str:
        """
        컨텍스트를 AI 프롬프트용 텍스트로 변환

        Args:
            context: build_hero_context()의 반환값

        Returns:
            포맷팅된 프롬프트 문자열
        """
        hero = context["hero"]
        talent_mechanics = context["talent_mechanics"]
        skills = context["available_skills"]
        items = context["available_items"]
        user_prefs = context["user_preferences"]

        prompt_parts = []

        # 1. 영웅 정보
        prompt_parts.append("# HERO INFORMATION")
        prompt_parts.append(f"Name: {hero['name']}")
        prompt_parts.append(f"Talent: {hero['talent']}")
        prompt_parts.append(f"God Type: {hero['god_type']}")
        if hero.get('description'):
            prompt_parts.append(f"Description: {hero['description']}")
        prompt_parts.append("")

        # 2. 재능 메커니즘 (핵심!)
        prompt_parts.append("# TALENT MECHANICS (CRITICAL)")
        for tl in talent_mechanics:
            prompt_parts.append(f"Level {tl['level']} - {tl['effect_name']}:")
            prompt_parts.append(f"  {tl['effect_description']}")
            if tl['mechanics']:
                prompt_parts.append(f"  Keywords: {', '.join(tl['mechanics'])}")
        prompt_parts.append("")

        # 3. 사용 가능한 스킬
        prompt_parts.append(f"# AVAILABLE SKILLS (Total: {len(skills)})")
        for skill in skills[:30]:  # 최대 30개만 포함
            prompt_parts.append(f"- {skill['name']} ({skill['type']})")
            prompt_parts.append(f"  Damage: {skill['damage_type']}, Tags: {', '.join(skill['tags'][:5])}")
            if skill.get('description'):
                prompt_parts.append(f"  Description: {skill['description']}")
            if skill.get('playstyle_match'):
                prompt_parts.append(f"  ⭐ MATCHES USER PLAYSTYLE")
        prompt_parts.append("")

        # 4. 사용 가능한 아이템
        prompt_parts.append(f"# AVAILABLE ITEMS (Total: {len(items)})")
        for item in items[:20]:  # 최대 20개만 포함
            prompt_parts.append(f"- {item['name']} ({item['slot']}, {item['rarity']})")
            prompt_parts.append(f"  Stat: {item['stat_type']}, Type: {item['type']}")
            if item.get('set_name'):
                prompt_parts.append(f"  Set: {item['set_name']}")
            if item.get('special_effects') and len(item['special_effects']) > 0:
                effects_str = str(item['special_effects'][0])[:100]  # 첫 효과만
                prompt_parts.append(f"  Effect: {effects_str}")
        prompt_parts.append("")

        # 5. 사용자 선호도
        if user_prefs.get('playstyle'):
            prompt_parts.append("# USER PREFERENCES")
            prompt_parts.append(f"Preferred Playstyle: {user_prefs['playstyle']}")
            prompt_parts.append("")

        return "\n".join(prompt_parts)
