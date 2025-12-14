"""
Game Mechanics Analyzer
메커니즘 기반 스킬/아이템 분석 및 시너지 평가
"""
from typing import List, Dict, Set, Tuple
import json


class MechanicsAnalyzer:
    """게임 메커니즘 기반 분석기"""

    # Damage type to ailment mapping
    DAMAGE_TO_AILMENT = {
        "Physical": "Trauma",
        "Fire": "Ignite",
        "Cold": "Frostbite",
        "Lightning": "Shock",
        "Erosion": "Wilt"
    }

    # DoT ailments (requires different build strategy)
    DOT_AILMENTS = {"Trauma", "Ignite", "Wilt"}

    # Hit-based ailments
    HIT_AILMENTS = {"Shock", "Frostbite"}

    def __init__(self):
        pass

    def analyze_skill_mechanics(self, skill: Dict) -> Dict:
        """
        스킬의 메커니즘 특성 분석

        Returns:
            {
                'is_dot': bool,
                'is_hit': bool,
                'damage_type': str,
                'ailment': str,
                'mechanics': Set[str],
                'build_style': str  # 'DoT', 'Hit', 'Hybrid'
            }
        """
        result = {
            'is_dot': False,
            'is_hit': False,
            'damage_type': skill.get('damage_type'),
            'ailment': None,
            'mechanics': set(),
            'build_style': 'Unknown'
        }

        # Parse tags
        tags = []
        if skill.get('tags'):
            try:
                tags = json.loads(skill['tags']) if isinstance(skill['tags'], str) else skill['tags']
            except:
                tags = []

        tags_lower = [tag.lower() for tag in tags]
        desc_lower = (skill.get('description') or '').lower()

        # Detect DoT
        dot_keywords = ['damage over time', 'dot', 'per second', 'ignite', 'trauma',
                        'wilt', 'burning', 'bleed', 'poison', 'erosion']
        if any(kw in tags_lower for kw in ['dot', 'ailment']) or \
           any(kw in desc_lower for kw in dot_keywords):
            result['is_dot'] = True
            result['build_style'] = 'DoT'

        # Detect Hit-based
        hit_keywords = ['hit', 'strike', 'attack', 'cast']
        if any(kw in tags_lower for kw in hit_keywords) or \
           'hit' in desc_lower:
            result['is_hit'] = True
            if not result['is_dot']:
                result['build_style'] = 'Hit'
            else:
                result['build_style'] = 'Hybrid'

        # Determine ailment
        if result['damage_type']:
            result['ailment'] = self.DAMAGE_TO_AILMENT.get(result['damage_type'])

        # Detect special mechanics
        if any('spell burst' in tag.lower() for tag in tags):
            result['mechanics'].add('Spell Burst')
        if any('multistrike' in tag.lower() for tag in tags):
            result['mechanics'].add('Multistrike')
        if any('combo' in tag.lower() for tag in tags):
            result['mechanics'].add('Combo')
        if any('channel' in tag.lower() for tag in tags):
            result['mechanics'].add('Channeled')
        if any('chain' in tag.lower() for tag in tags):
            result['mechanics'].add('Chain')
        if any('aoe' in tag.lower() or 'area' in tag.lower() for tag in tags):
            result['mechanics'].add('AoE')
        if any('melee' in tag.lower() for tag in tags):
            result['mechanics'].add('Melee')
        if any('ranged' in tag.lower() for tag in tags):
            result['mechanics'].add('Ranged')

        return result

    def get_recommended_stats(self, skill_analysis: Dict) -> List[str]:
        """
        스킬 분석 결과 기반 추천 스탯 리스트

        Args:
            skill_analysis: analyze_skill_mechanics()의 결과

        Returns:
            추천 스탯 리스트
        """
        stats = []

        # DoT build
        if skill_analysis['build_style'] in ['DoT', 'Hybrid']:
            stats.extend([
                'Affliction',  # DoT damage multiplier
                'Reaping',     # Instant DoT damage
                'Damage Over Time',
                f"{skill_analysis['damage_type']} Damage" if skill_analysis['damage_type'] else None
            ])

            # Specific ailment stats
            if skill_analysis['ailment'] == 'Ignite':
                stats.extend([
                    'Single Hit Damage',  # Ignite doesn't stack
                    'Ignite Damage',
                    'Fire Damage'
                ])
            elif skill_analysis['ailment'] == 'Wilt':
                stats.extend([
                    'Attack Speed',  # Stack Wilt fast
                    'Erosion Damage',
                    'Wilt Damage'
                ])
            elif skill_analysis['ailment'] == 'Trauma':
                stats.extend([
                    'Physical Damage',
                    'Trauma Damage',
                    'Reaping'
                ])

        # Hit build
        if skill_analysis['build_style'] in ['Hit', 'Hybrid']:
            stats.extend([
                'Critical Strike Chance',
                'Critical Strike Damage',
                'Damage',
                f"{skill_analysis['damage_type']} Damage" if skill_analysis['damage_type'] else None
            ])

            # Multistrike synergy
            if 'Multistrike' in skill_analysis['mechanics']:
                stats.extend([
                    'Attack Speed',
                    'Multistrike Chance'
                ])

        # Spell Burst
        if 'Spell Burst' in skill_analysis['mechanics']:
            stats.extend([
                'Spell Burst Damage',
                'Spell Damage',
                'Cooldown Recovery'
            ])

        # AoE
        if 'AoE' in skill_analysis['mechanics']:
            stats.extend([
                'Area Damage',
                'Area of Effect'
            ])

        # Remove None and duplicates
        stats = list(set(filter(None, stats)))
        return stats

    def calculate_synergy_score(
        self,
        skill_analyses: List[Dict],
        item_effects: List[str]
    ) -> Tuple[float, List[str]]:
        """
        스킬들과 아이템 효과 간의 시너지 점수 계산

        Args:
            skill_analyses: analyze_skill_mechanics() 결과 리스트
            item_effects: 아이템 효과 문자열 리스트

        Returns:
            (synergy_score, reasons)
        """
        score = 0.0
        reasons = []

        if not skill_analyses:
            return 0.0, []

        # Determine dominant build style
        dot_count = sum(1 for s in skill_analyses if s['build_style'] == 'DoT')
        hit_count = sum(1 for s in skill_analyses if s['build_style'] == 'Hit')
        total = len(skill_analyses)

        if dot_count / total > 0.6:
            dominant_style = 'DoT'
        elif hit_count / total > 0.6:
            dominant_style = 'Hit'
        else:
            dominant_style = 'Hybrid'

        # Collect all recommended stats
        all_recommended_stats = set()
        for analysis in skill_analyses:
            all_recommended_stats.update(self.get_recommended_stats(analysis))

        # Check item effects match
        item_effects_lower = ' '.join(item_effects).lower()

        matches = 0
        for stat in all_recommended_stats:
            if stat and stat.lower() in item_effects_lower:
                matches += 1
                score += 10
                reasons.append(f"✓ {stat} synergy")

        # Build coherence bonus
        if dominant_style == 'DoT':
            if 'affliction' in item_effects_lower:
                score += 15
                reasons.append("✓ Affliction (DoT multiplier)")
            if 'reaping' in item_effects_lower:
                score += 15
                reasons.append("✓ Reaping (instant DoT damage)")
            if 'critical' in item_effects_lower:
                score -= 5
                reasons.append("⚠ Critical (not valuable for DoT)")

        elif dominant_style == 'Hit':
            if 'critical' in item_effects_lower:
                score += 15
                reasons.append("✓ Critical Strike (Hit build essential)")
            if 'multistrike' in item_effects_lower:
                score += 10
                reasons.append("✓ Multistrike (free extra attacks)")
            if 'affliction' in item_effects_lower and 'reaping' not in item_effects_lower:
                score -= 5
                reasons.append("⚠ Affliction (better for DoT builds)")

        # Multiplicative bonus detection
        multiplicative_keywords = ['additional', 'more', 'multiplied']
        if any(kw in item_effects_lower for kw in multiplicative_keywords):
            score += 20
            reasons.append("✓✓ Multiplicative bonus (high value!)")

        return min(score, 100), reasons

    def get_build_type_from_skills(self, skill_analyses: List[Dict]) -> str:
        """
        스킬 분석 결과로부터 빌드 타입 결정

        Returns:
            'DoT', 'Hit', 'Hybrid', 'Unknown'
        """
        if not skill_analyses:
            return 'Unknown'

        dot_count = sum(1 for s in skill_analyses if s['build_style'] == 'DoT')
        hit_count = sum(1 for s in skill_analyses if s['build_style'] == 'Hit')
        total = len(skill_analyses)

        if total == 0:
            return 'Unknown'

        dot_ratio = dot_count / total
        hit_ratio = hit_count / total

        if dot_ratio >= 0.7:
            return 'DoT'
        elif hit_ratio >= 0.7:
            return 'Hit'
        elif dot_ratio >= 0.3 or hit_ratio >= 0.3:
            return 'Hybrid'
        else:
            return 'Unknown'

    def get_playstyle_tips(self, build_type: str, dominant_damage: str = None) -> List[str]:
        """
        빌드 타입 기반 플레이 팁 생성

        Args:
            build_type: 'DoT', 'Hit', 'Hybrid'
            dominant_damage: 주 데미지 타입

        Returns:
            플레이 팁 리스트
        """
        tips = []

        if build_type == 'DoT':
            tips.extend([
                "Apply ailments quickly and let damage over time do the work",
                "Prioritize Affliction and Reaping stats for maximum DoT damage",
                "Critical Strike is less valuable - focus on DoT modifiers instead"
            ])

            if dominant_damage == 'Fire':
                tips.append("Ignite doesn't stack - use high single-hit damage skills")
            elif dominant_damage == 'Erosion':
                tips.append("Wilt stacks infinitely - attack as fast as possible")
            elif dominant_damage == 'Physical':
                tips.append("Use Reaping to instantly deal Trauma damage")

        elif build_type == 'Hit':
            tips.extend([
                "Maximize Critical Strike Chance and Damage for burst",
                "Look for Multistrike to gain free extra attacks",
                "Attack speed and hit damage are your priority stats"
            ])

        elif build_type == 'Hybrid':
            tips.extend([
                "Balance between Hit damage and DoT scaling",
                "Use hits to apply ailments, then let DoT finish enemies",
                "Prioritize skills that benefit from both playstyles"
            ])

        return tips
