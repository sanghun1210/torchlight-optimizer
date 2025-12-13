"""
빌드 추천 엔진 v2 - 게임 메커니즘 기반
"""
import json
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from collections import Counter

from backend.database.models import Hero, Skill, Item, TalentNode, TalentLevel
from backend.game_mechanics import (
    DAMAGE_TYPES, DAMAGE_FORMS, AILMENTS, SKILL_TAG_SYNERGIES,
    STAT_EFFECTS, SPELL_BURST, COMBO,
    get_primary_stat_for_god_type,
    should_avoid_crit_for_skill,
    get_skill_speed_type,
    get_ailment_for_damage_type,
    get_recommended_stats_for_skill_tags,
    get_recommended_stats_for_damage_form,
    get_recommended_stats_for_ailment,
    is_spell_burst_compatible,
    is_combo_skill,
    is_dot_ailment,
    should_focus_on_stacking
)
from backend.talent_mechanics import (
    get_talent_mechanics,
    get_talent_build_focus,
    get_talent_must_have_mechanics,
    get_talent_avoid_mechanics,
    get_recommended_skill_types,
    get_recommended_item_stats,
    is_burst_focused_talent,
    get_talent_playstyle
)


class RecommendationEngineV2:
    """빌드 추천 엔진 v2 - 게임 메커니즘 활용"""

    def __init__(self, db: Session):
        self.db = db
        self._talent_level_cache = {}  # 재능 레벨 효과 캐시

    def recommend_build(
        self,
        hero_id: int,
        playstyle: Optional[str] = None,
        focus: Optional[str] = None,
        max_skills: int = 6,
        max_items: int = 10
    ) -> Dict:
        """
        영웅 기반 빌드 추천 (v2)

        Args:
            hero_id: 영웅 ID
            playstyle: 플레이스타일
            focus: 빌드 초점
            max_skills: 추천할 최대 스킬 개수
            max_items: 추천할 최대 아이템 개수

        Returns:
            추천 빌드 딕셔너리
        """
        # 영웅 정보
        hero = self.db.query(Hero).filter(Hero.id == hero_id).first()
        if not hero:
            raise ValueError(f"Hero with id {hero_id} not found")

        # 영웅의 주 스탯 결정
        primary_stat = get_primary_stat_for_god_type(hero.god_type)

        # 스킬 추천
        recommended_skills = self._recommend_skills_v2(hero, playstyle, max_skills)

        # 빌드 타입 분석 (DoT/Hit/Hybrid)
        build_type = self._analyze_build_type(recommended_skills)

        # 아이템 추천 (빌드 타입 기반)
        recommended_items = self._recommend_items_v2(
            hero, recommended_skills, build_type, primary_stat, max_items
        )

        # 재능 노드 추천
        recommended_talents = self._recommend_talent_nodes_v2(hero, build_type, max_nodes=5)

        # 시너지 점수 계산 (v2)
        synergy_score = self._calculate_synergy_score_v2(
            recommended_skills, recommended_items, build_type
        )

        return {
            "hero_id": hero.id,
            "hero_name": hero.name,
            "hero_talent": hero.talent,
            "god_type": hero.god_type,
            "primary_stat": primary_stat,
            "build_type": build_type,
            "recommended_skills": recommended_skills,
            "recommended_items": recommended_items,
            "recommended_talents": recommended_talents,
            "synergy_score": round(synergy_score, 2),
            "build_summary": self._generate_build_summary_v2(
                hero, recommended_skills, recommended_items, build_type
            )
        }

    def _recommend_skills_v2(
        self,
        hero: Hero,
        playstyle: Optional[str],
        max_skills: int
    ) -> List[Dict]:
        """스킬 추천 v2 - 게임 메커니즘 기반"""
        all_skills = self.db.query(Skill).all()
        scored_skills = []

        # 영웅의 주 스탯 기반 선호 데미지 타입
        primary_stat = get_primary_stat_for_god_type(hero.god_type)
        preferred_damage_types = self._get_preferred_damage_types(primary_stat, hero.god_type)

        # 재능 메커니즘 가져오기
        talent_mechanics = get_talent_mechanics(hero.talent)
        must_have_mechanics = get_talent_must_have_mechanics(hero.talent)
        avoid_mechanics = get_talent_avoid_mechanics(hero.talent)
        recommended_skill_types = get_recommended_skill_types(hero.talent)
        is_burst_talent = is_burst_focused_talent(hero.talent)

        # DB에서 재능 레벨 효과 조회
        has_60_penalty = self._has_critical_level_60_penalty(hero.talent)
        talent_level_mechanics = self._get_talent_level_mechanics(hero.talent)

        for skill in all_skills:
            score = 0
            reasons = []
            skill_tags = []

            # 태그 파싱
            if skill.tags:
                try:
                    skill_tags = json.loads(skill.tags)
                except json.JSONDecodeError:
                    skill_tags = []

            # 1. 스킬 타입 기본 점수
            if skill.type == "Active Skill":
                score += 15
                reasons.append("핵심 액티브 스킬")
            elif skill.type == "Support Skill":
                score += 8
                reasons.append("서포트 스킬")

            # 2. DoT vs Hit 구분 (강화)
            is_dot = False

            # 태그 기반 DoT 감지
            dot_keywords_in_tags = ["DoT", "Damage Over Time", "Ailment", "Burn", "Bleed", "Poison"]
            for keyword in dot_keywords_in_tags:
                if any(keyword.lower() in tag.lower() for tag in skill_tags):
                    is_dot = True
                    break

            # 설명 기반 DoT 감지 (강화)
            if skill.description:
                desc_lower = skill.description.lower()
                dot_keywords_in_desc = [
                    "damage over time", "dot", "per second",
                    "ignite", "trauma", "wilt", "bleed", "poison",
                    "burning", "erosion", "affliction"
                ]
                for keyword in dot_keywords_in_desc:
                    if keyword in desc_lower:
                        is_dot = True
                        break

            # 데미지 타입 기반 DoT 유추 (보조)
            if skill.damage_type in ["Fire", "Erosion"] and not is_dot:
                # Fire와 Erosion은 DoT 경향이 있음
                if skill.description and "over time" in skill.description.lower():
                    is_dot = True

            if is_dot:
                score += 5
                reasons.append("DoT 스킬")
            else:
                score += 3
                reasons.append("Hit 스킬")

            # 3. 데미지 타입 점수
            if skill.damage_type:
                score += 5
                reasons.append(f"{skill.damage_type} 데미지")

                # 영웅 선호 데미지 타입 보너스
                if skill.damage_type in preferred_damage_types:
                    bonus = 10 - preferred_damage_types.index(skill.damage_type) * 2  # 순서대로 10, 8, 6...
                    score += bonus
                    reasons.append(f"{hero.god_type} 최적 데미지")

                # 상태이상 시너지
                ailment = get_ailment_for_damage_type(skill.damage_type)
                if ailment and ailment != "Unknown":
                    score += 3
                    reasons.append(f"{ailment} 상태이상")

            # 4. 플레이스타일 매칭 (강화)
            if playstyle:
                playstyle_lower = playstyle.lower()
                for tag in skill_tags:
                    if playstyle_lower in tag.lower():
                        score += 10
                        reasons.append(f"{playstyle} 완벽 매칭")
                        break

            # 5. 스킬 태그 시너지
            tag_synergies = get_recommended_stats_for_skill_tags(skill_tags)
            if tag_synergies:
                score += len(tag_synergies) * 0.5
                reasons.append(f"{len(tag_synergies)}개 시너지 스탯")

            # 6. Spell Burst 호환성
            if is_spell_burst_compatible(skill_tags):
                score += 5
                reasons.append("Spell Burst 가능")

            # 7. Combo 스킬
            if is_combo_skill(skill_tags):
                score += 7
                reasons.append("Combo 스킬 (곱셈 스케일)")

            # 8. 재능 메커니즘 기반 스코어링 ⭐ 중요!
            if talent_mechanics:
                # 8-1. 필수 메커니즘 체크
                for must_have in must_have_mechanics:
                    must_have_lower = must_have.lower()

                    # 스킬 타입에서 매칭
                    if skill.type and must_have_lower in skill.type.lower():
                        score += 20
                        reasons.append(f"재능 필수: {must_have}")
                        continue

                    # 스킬 태그에서 매칭
                    if any(must_have_lower in tag.lower() for tag in skill_tags):
                        score += 20
                        reasons.append(f"재능 필수: {must_have}")
                        continue

                    # 설명에서 매칭 (약한 신호)
                    if skill.description and must_have_lower in skill.description.lower():
                        score += 10
                        reasons.append(f"재능 권장: {must_have}")

                # 8-2. 피해야 할 메커니즘 체크
                for avoid in avoid_mechanics:
                    avoid_lower = avoid.lower()

                    # DoT 스킬인데 DoT를 피해야 하는 경우
                    if "dot" in avoid_lower and is_dot:
                        score -= 25  # 강한 패널티
                        reasons.append(f"⚠️ 재능 비추천: DoT 스킬")

                    # Spell 스킬인데 Spell을 피해야 하는 경우
                    if "spell" in avoid_lower:
                        if any("spell" in tag.lower() for tag in skill_tags):
                            score -= 20
                            reasons.append(f"⚠️ 재능 비추천: Spell")

                    # Non-Burst 스킬 체크 (Burst 재능의 경우)
                    if "non-burst" in avoid_lower:
                        # Melee Attack이 아니면 페널티
                        is_melee_attack = any("melee" in tag.lower() or "attack" in tag.lower() for tag in skill_tags)
                        if not is_melee_attack:
                            score -= 30  # 매우 강한 패널티 (Anger의 -80%를 반영)
                            reasons.append(f"⚠️ Burst 재능에 부적합")

                # 8-3. 추천 스킬 타입 매칭
                for recommended_type in recommended_skill_types:
                    recommended_lower = recommended_type.lower()

                    # 스킬 타입 직접 매칭
                    if skill.type and recommended_lower in skill.type.lower():
                        score += 15
                        reasons.append(f"재능 최적: {recommended_type}")
                        continue

                    # 태그 매칭
                    if any(recommended_lower in tag.lower() for tag in skill_tags):
                        score += 15
                        reasons.append(f"재능 최적: {recommended_type}")
                        continue

                # 8-4. Burst 재능 특화 (Anger 등)
                if is_burst_talent:
                    # Melee + Attack 조합 = Burst 트리거 가능
                    has_melee = any("melee" in tag.lower() for tag in skill_tags)
                    has_attack = any("attack" in tag.lower() for tag in skill_tags)
                    has_aoe = any("aoe" in tag.lower() or "area" in tag.lower() for tag in skill_tags)

                    if has_melee and has_attack:
                        score += 25
                        reasons.append("✅ Burst 트리거 (Melee Attack)")

                    if has_aoe:
                        score += 15
                        reasons.append("✅ Burst 데미지 증가 (Area)")

                # 8-5. 60레벨 크리티컬 패널티 반영 ⚠️
                if has_60_penalty:
                    # Burst 재능의 경우 non-Burst 스킬에 매우 강한 패널티
                    if is_burst_talent:
                        is_burst_compatible = any("melee" in tag.lower() and "attack" in tag.lower() for tag in skill_tags)
                        if not is_burst_compatible:
                            score -= 40  # Tunnel Vision 반영 (-80% 패널티)
                            reasons.append("⚠️⚠️ 60레벨 패널티: Burst 불가 스킬")

                # 8-6. 레벨별 메커니즘 추가 보너스
                for level, mechs in talent_level_mechanics.items():
                    if level >= 60:  # 60레벨 이상의 중요한 메커니즘
                        for mech in mechs:
                            # 스킬이 해당 메커니즘을 지원하면 보너스
                            if mech in ["melee", "attack_speed", "critical", "area"]:
                                if any(mech in tag.lower() for tag in skill_tags):
                                    score += 5
                                    reasons.append(f"Lv{level} 메커니즘: {mech}")

            # 9. 설명 품질 (데이터 완성도)
            if skill.description and len(skill.description) > 100:
                score += 2

            scored_skills.append({
                "skill_id": skill.id,
                "skill_name": skill.name,
                "skill_type": skill.type,
                "damage_type": skill.damage_type,
                "tags": skill.tags,
                "is_dot": is_dot,
                "is_spell_burst_compatible": is_spell_burst_compatible(skill_tags),
                "is_combo": is_combo_skill(skill_tags),
                "score": score,
                "reason": ", ".join(reasons) if reasons else "기본 추천",
                "priority": self._calculate_skill_priority(score, is_dot)
            })

        # 점수순 정렬
        scored_skills.sort(key=lambda x: x["score"], reverse=True)
        return scored_skills[:max_skills]

    def _recommend_items_v2(
        self,
        hero: Hero,
        recommended_skills: List[Dict],
        build_type: str,
        primary_stat: str,
        max_items: int
    ) -> List[Dict]:
        """아이템 추천 v2 - 빌드 타입 기반"""
        all_items = self.db.query(Item).all()
        scored_items = []

        # 스킬 분석
        damage_types = [s.get("damage_type") for s in recommended_skills if s.get("damage_type")]
        primary_damage = Counter(damage_types).most_common(1)
        primary_damage_type = primary_damage[0][0] if primary_damage else None

        # 상태이상 분석
        primary_ailment = None
        if primary_damage_type:
            primary_ailment = get_ailment_for_damage_type(primary_damage_type)

        # DoT 빌드 여부
        is_dot_build = build_type in ["DoT", "Hybrid_DoT"]

        # 재능 메커니즘 가져오기
        talent_mechanics = get_talent_mechanics(hero.talent)
        recommended_item_stats_list = get_recommended_item_stats(hero.talent)
        is_burst_talent = is_burst_focused_talent(hero.talent)

        for item in all_items:
            score = 0
            reasons = []

            # 1. Stat Type 매칭 (강화)
            if item.stat_type == primary_stat:
                score += 15
                reasons.append(f"{primary_stat} 스탯 매칭")

            # 2. 레전더리 우선
            if item.rarity == "Legendary":
                score += 8
                reasons.append("레전더리")

            # 3. 세트 아이템
            if item.set_name:
                score += 5
                reasons.append(f"{item.set_name} 세트")

            # 4. 데미지 타입 시너지
            if primary_damage_type and item.special_effects:
                effects_lower = item.special_effects.lower()

                # 정확한 데미지 타입 매칭
                if primary_damage_type.lower() in effects_lower:
                    score += 10
                    reasons.append(f"{primary_damage_type} 강화")

                # 상태이상 시너지
                if primary_ailment:
                    ailment_lower = primary_ailment.lower()
                    if ailment_lower in effects_lower:
                        score += 8
                        reasons.append(f"{primary_ailment} 시너지")

            # 5. DoT 빌드 최적화
            if is_dot_build and item.special_effects:
                effects_lower = item.special_effects.lower()

                # DoT 관련 스탯
                dot_keywords = ["affliction", "reaping", "damage over time", "dot"]
                for keyword in dot_keywords:
                    if keyword in effects_lower:
                        score += 12
                        reasons.append(f"DoT 최적화 ({keyword})")
                        break

                # 크리티컬 아이템 패널티
                crit_keywords = ["critical", "crit"]
                for keyword in crit_keywords:
                    if keyword in effects_lower:
                        score -= 5
                        reasons.append("DoT 빌드에 크리티컬 불필요")
                        break

            # 6. Hit 빌드 최적화
            if not is_dot_build and item.special_effects:
                effects_lower = item.special_effects.lower()

                # 크리티컬/더블 데미지
                if "critical" in effects_lower or "crit" in effects_lower:
                    score += 10
                    reasons.append("크리티컬 강화")

                if "double damage" in effects_lower:
                    score += 8
                    reasons.append("더블 데미지")

            # 7. Spell Burst/Combo 특화
            has_spell_burst = any(s.get("is_spell_burst_compatible") for s in recommended_skills)
            has_combo = any(s.get("is_combo") for s in recommended_skills)

            if has_spell_burst and item.special_effects:
                if "spell burst" in item.special_effects.lower():
                    score += 15
                    reasons.append("Spell Burst 특화")

            if has_combo and item.special_effects:
                if "combo" in item.special_effects.lower():
                    score += 15
                    reasons.append("Combo 특화")

            # 8. 재능 메커니즘 기반 아이템 스코어링 ⭐ 중요!
            if talent_mechanics and item.special_effects:
                effects_lower = item.special_effects.lower()

                # 8-1. 추천 아이템 스탯 매칭
                for recommended_stat in recommended_item_stats_list:
                    stat_lower = recommended_stat.lower()

                    if stat_lower in effects_lower:
                        score += 12
                        reasons.append(f"재능 최적 스탯: {recommended_stat}")

                # 8-2. Burst 재능 특화 (Anger 등)
                if is_burst_talent:
                    # Attack Speed = Burst 쿨다운 감소
                    if "attack speed" in effects_lower:
                        score += 18
                        reasons.append("✅ Burst 쿨다운 감소")

                    # Critical Strike = Rage 생성
                    if "critical" in effects_lower or "crit" in effects_lower:
                        score += 15
                        reasons.append("✅ Rage 생성 (Crit)")

                    # Area = Burst 데미지 증가
                    if "area" in effects_lower or "aoe" in effects_lower:
                        score += 15
                        reasons.append("✅ Burst 데미지 증가 (Area)")

                    # Burst Damage 직접 증가
                    if "burst" in effects_lower:
                        score += 20
                        reasons.append("✅ Burst 데미지 직접 증가")

                    # Melee Damage
                    if "melee" in effects_lower:
                        score += 12
                        reasons.append("✅ Melee 데미지 증가")

                    # Rage Generation
                    if "rage" in effects_lower:
                        score += 15
                        reasons.append("✅ Rage 생성 증가")

                    # Cooldown Recovery
                    if "cooldown" in effects_lower and "recovery" in effects_lower:
                        score += 15
                        reasons.append("✅ 쿨다운 회복")

            scored_items.append({
                "item_id": item.id,
                "item_name": item.name,
                "slot": item.slot,
                "type": item.type,
                "rarity": item.rarity,
                "stat_type": item.stat_type,
                "set_name": item.set_name,
                "score": score,
                "reason": ", ".join(reasons) if reasons else "기본 추천"
            })

        # 점수순 정렬
        scored_items.sort(key=lambda x: x["score"], reverse=True)

        # 슬롯별 균형
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

    def _recommend_talent_nodes_v2(
        self,
        hero: Hero,
        build_type: str,
        max_nodes: int = 5
    ) -> List[Dict]:
        """재능 노드 추천 v2"""
        all_nodes = self.db.query(TalentNode).all()
        scored_nodes = []

        for node in all_nodes:
            score = 0
            reasons = []

            # 1. Core 노드 우선
            if node.node_type == "Core":
                score += 15
                reasons.append("코어 노드")
            else:
                score += 5

            # 2. God Class 매칭
            if node.god_class and hero.god_type:
                if hero.god_type.lower() in node.god_class.lower():
                    score += 12
                    reasons.append(f"{hero.god_type} 매칭")

            # 3. Tier 점수
            if node.tier:
                if "Legendary" in node.tier:
                    score += 8
                    reasons.append("레전더리 노드")
                elif "Large" in node.tier:
                    score += 6
                    reasons.append("대형 노드")
                elif "Medium" in node.tier:
                    score += 4
                    reasons.append("중형 노드")

            # 4. 빌드 타입 매칭
            if node.effect and build_type:
                effect_lower = node.effect.lower()

                if "DoT" in build_type:
                    if any(kw in effect_lower for kw in ["affliction", "reaping", "damage over time"]):
                        score += 10
                        reasons.append("DoT 빌드 시너지")

                if "Hit" in build_type:
                    if any(kw in effect_lower for kw in ["critical", "attack", "hit"]):
                        score += 10
                        reasons.append("Hit 빌드 시너지")

            scored_nodes.append({
                "node_id": node.id,
                "node_name": node.name,
                "node_type": node.node_type,
                "tier": node.tier,
                "god_class": node.god_class,
                "score": score,
                "reason": ", ".join(reasons) if reasons else "기본 추천"
            })

        scored_nodes.sort(key=lambda x: x["score"], reverse=True)
        return scored_nodes[:max_nodes]

    def _analyze_build_type(self, skills: List[Dict]) -> str:
        """추천된 스킬들을 분석하여 빌드 타입 결정"""
        dot_count = sum(1 for s in skills if s.get("is_dot"))
        total = len(skills)

        if total == 0:
            return "Unknown"

        dot_ratio = dot_count / total

        if dot_ratio >= 0.7:
            return "DoT"
        elif dot_ratio >= 0.3:
            return "Hybrid_DoT"
        else:
            return "Hit"

    def _calculate_skill_priority(self, score: float, is_dot: bool) -> int:
        """스킬 우선순위 계산"""
        if score >= 30:
            return 1  # 최우선
        elif score >= 20:
            return 2  # 높음
        elif score >= 10:
            return 3  # 보통
        else:
            return 4  # 낮음

    def _calculate_synergy_score_v2(
        self,
        skills: List[Dict],
        items: List[Dict],
        build_type: str
    ) -> float:
        """시너지 점수 계산 v2"""
        synergy = 0.0

        # 1. 빌드 일관성 보너스
        if build_type == "DoT":
            synergy += 20  # 순수 DoT 빌드
        elif build_type == "Hit":
            synergy += 20  # 순수 Hit 빌드
        elif build_type == "Hybrid_DoT":
            synergy += 10  # 하이브리드

        # 2. 데미지 타입 일관성
        damage_types = [s.get("damage_type") for s in skills if s.get("damage_type")]
        if damage_types:
            most_common = Counter(damage_types).most_common(1)[0]
            consistency_ratio = most_common[1] / len(damage_types)
            synergy += consistency_ratio * 25

        # 3. 스킬 개수
        synergy += min(len(skills) * 4, 20)

        # 4. 아이템 개수
        synergy += min(len(items) * 2, 15)

        # 5. 세트 아이템 보너스
        set_items = [i for i in items if i.get("set_name")]
        synergy += len(set_items) * 3

        # 6. 특수 메커니즘 보너스
        has_spell_burst = any(s.get("is_spell_burst_compatible") for s in skills)
        has_combo = any(s.get("is_combo") for s in skills)

        if has_spell_burst:
            synergy += 5
        if has_combo:
            synergy += 5

        return min(synergy, 100.0)

    def _generate_build_summary_v2(
        self,
        hero: Hero,
        skills: List[Dict],
        items: List[Dict],
        build_type: str
    ) -> str:
        """빌드 요약 생성 v2"""
        damage_types = [s.get("damage_type") for s in skills if s.get("damage_type")]
        primary_damage = Counter(damage_types).most_common(1)

        if primary_damage:
            damage_focus = primary_damage[0][0]
            ailment = get_ailment_for_damage_type(damage_focus)
        else:
            damage_focus = "혼합"
            ailment = None

        summary = f"{hero.name} ({hero.talent}) - {build_type} 빌드"
        summary += f" | {damage_focus} 데미지"

        if ailment and ailment != "Unknown":
            summary += f" | {ailment} 활용"

        set_count = len([i for i in items if i.get("set_name")])
        if set_count > 0:
            summary += f" | {set_count}개 세트"

        # 특수 메커니즘
        if any(s.get("is_spell_burst_compatible") for s in skills):
            summary += " | Spell Burst"
        if any(s.get("is_combo") for s in skills):
            summary += " | Combo"

        return summary

    def _get_preferred_damage_types(self, primary_stat: str, god_type: str) -> List[str]:
        """영웅의 주 스탯과 God Type에 따른 선호 데미지 타입"""
        preferences = []

        # STR 기반 (물리, 화염)
        if primary_stat == "STR":
            preferences = ["Physical", "Fire"]
            if "Berserker" in god_type:
                preferences.insert(0, "Physical")  # Physical 최우선

        # DEX 기반 (번개, 냉기)
        elif primary_stat == "DEX":
            preferences = ["Lightning", "Cold", "Physical"]

        # INT 기반 (원소)
        elif primary_stat == "INT":
            preferences = ["Fire", "Cold", "Lightning", "Erosion"]

        return preferences

    def _get_talent_level_effects(self, talent_name: str) -> List[TalentLevel]:
        """
        재능의 모든 레벨 효과 조회 (DB에서 크롤링된 데이터)

        Args:
            talent_name: 재능 이름

        Returns:
            재능 레벨 효과 리스트
        """
        # 캐시 확인
        if talent_name in self._talent_level_cache:
            return self._talent_level_cache[talent_name]

        # DB 조회
        talent_levels = self.db.query(TalentLevel).filter(
            TalentLevel.talent_name == talent_name
        ).order_by(TalentLevel.level).all()

        # 캐시 저장
        self._talent_level_cache[talent_name] = talent_levels

        return talent_levels

    def _has_critical_level_60_penalty(self, talent_name: str) -> bool:
        """
        60레벨에 중요한 패널티가 있는지 확인

        Args:
            talent_name: 재능 이름

        Returns:
            60레벨 패널티 존재 여부
        """
        talent_levels = self._get_talent_level_effects(talent_name)

        for level in talent_levels:
            if level.level == 60:
                desc_lower = level.effect_description.lower()
                # -80%, -50% 같은 큰 패널티 확인
                if '-80%' in desc_lower or '-50%' in desc_lower:
                    return True

                # "non-" 패턴 확인 (non-Burst, non-DoT 등)
                if 'non-' in desc_lower and 'damage' in desc_lower:
                    return True

        return False

    def _get_talent_level_mechanics(self, talent_name: str) -> Dict[str, List[str]]:
        """
        재능의 레벨별 메커니즘 추출

        Args:
            talent_name: 재능 이름

        Returns:
            레벨별 메커니즘 딕셔너리 {level: [mechanics]}
        """
        talent_levels = self._get_talent_level_effects(talent_name)
        level_mechanics = {}

        for level in talent_levels:
            try:
                mechanics = json.loads(level.mechanics) if level.mechanics else []
                level_mechanics[level.level] = mechanics
            except:
                level_mechanics[level.level] = []

        return level_mechanics
