"""
토치라이트 인피니트 게임 메커니즘 참조 데이터

출처: https://tlidb.com/en/Help
업데이트: 2024-12-13
"""

# ==============================================================================
# 데미지 타입 (Damage Types)
# ==============================================================================

DAMAGE_TYPES = {
    "Physical": {
        "bypasses_resistance": True,
        "ailment": "Trauma",
        "description": "물리 데미지는 저항을 무시함",
        "conversion_priority": 1  # 가장 낮음 (다른 타입으로 변환 가능)
    },
    "Lightning": {
        "bypasses_resistance": False,
        "ailment": "Shock",
        "description": "번개 데미지는 감전 상태이상 유발",
        "conversion_priority": 2
    },
    "Cold": {
        "bypasses_resistance": False,
        "ailment": "Frostbite/Freeze",
        "description": "냉기 데미지는 동상/빙결 유발 (군중 제어)",
        "crowd_control": True,
        "conversion_priority": 3
    },
    "Fire": {
        "bypasses_resistance": False,
        "ailment": "Ignite",
        "description": "화염 데미지는 점화 상태이상 유발 (DoT 중심)",
        "dot_focused": True,
        "conversion_priority": 4
    },
    "Erosion": {
        "bypasses_resistance": False,
        "ailment": "Wilt",
        "description": "부식 데미지",
        "conversion_priority": 5  # 가장 높음 (다른 타입으로 변환 불가)
    }
}

# 데미지 타입 변환 규칙
# Physical → Lightning → Cold → Fire → Erosion
# 낮은 우선순위에서 높은 우선순위로만 변환 가능
DAMAGE_CONVERSION_HIERARCHY = [
    "Physical", "Lightning", "Cold", "Fire", "Erosion"
]


# ==============================================================================
# 데미지 형태 (Damage Forms)
# ==============================================================================

DAMAGE_FORMS = {
    "Hit": {
        "description": "일반 공격/스펠 피해",
        "affected_by": [
            "Critical Strike",
            "Double Damage",
            "Accuracy/Evasion",
            "Armor",
            "Block",
            "Damage Type Conversion"
        ],
        "not_affected_by": [],
        "can_convert": True,  # 데미지 타입 변환 가능
        "recommended_stats": [
            "Critical Strike Chance",
            "Critical Damage",
            "Accuracy",
            "Armor Penetration",
            "Double Damage Chance"
        ]
    },
    "DoT": {
        "description": "지속 피해 (Damage Over Time)",
        "affected_by": [
            "Affliction",
            "Reaping",
            "Damage Type Conversion"
        ],
        "not_affected_by": [
            "Critical Strike",
            "Double Damage",
            "Accuracy",
            "Armor",
            "Block"
        ],
        "can_convert": False,  # Hit 데미지만 변환 가능
        "recommended_stats": [
            "Affliction",
            "Reaping",
            "DoT Multiplier",
            "Duration",
            "Ailment Chance"
        ]
    },
    "Secondary": {
        "description": "부수적 피해 (폭발 등)",
        "affected_by": [
            "Armor",
            "Avoidance",
            "Damage Type Conversion"
        ],
        "not_affected_by": [
            "Critical Strike",
            "Accuracy",
            "Block"
        ],
        "recommended_stats": [
            "Secondary Damage Boost",
            "Area Damage"
        ]
    },
    "Reflection": {
        "description": "반사 피해",
        "defensive_trigger": True
    },
    "True": {
        "description": "고정 비율 피해 (대부분 스탯 무시)",
        "ignores_most_modifiers": True,
        "percentage_based": True
    }
}


# ==============================================================================
# 데미지 계산 공식
# ==============================================================================

DAMAGE_CALCULATION = {
    "formula": "Damage = Base Damage × (1 + non-additional%) × (1 + add%₁) × (1 + add%₂) ...",
    "description": "비추가 보너스는 합산 후 1회 곱셈, 추가 보너스는 각각 독립적으로 곱셈",
    "modifier_types": {
        "non_additional": {
            "description": "일반 증가 보너스 (합산 후 1회 곱셈)",
            "example": "+30% Fire Damage, +20% Elemental Damage → (1 + 0.5) 곱셈"
        },
        "additional": {
            "description": "추가 보너스 (각각 독립 곱셈)",
            "example": "Additional 20% Damage, Additional 15% Damage → × 1.2 × 1.15",
            "priority": "높음 (곱셈 효과로 더 강력)"
        }
    }
}


# ==============================================================================
# 크리티컬 스트라이크 (Critical Strike)
# ==============================================================================

CRITICAL_STRIKE = {
    "applies_to": ["Hit"],  # Hit 데미지만
    "not_applies_to": ["DoT", "Secondary", "Reflection", "True"],
    "default_multiplier": 1.5,  # 150%
    "chance_formula": "Critical Chance = Critical Strike Rating / 100",
    "rating_formula": "Final Rating = Base × (1 + non-add%) × (1 + add%₁) × ...",
    "multi_hit_behavior": "멀티히트 스킬은 1회만 크리티컬 판정",
    "recommended_for": [
        "Hit Damage builds",
        "Attack Skills",
        "High frequency skills"
    ],
    "not_recommended_for": [
        "DoT builds",
        "Ailment-focused builds"
    ]
}


# ==============================================================================
# 더블 데미지 (Double Damage)
# ==============================================================================

DOUBLE_DAMAGE = {
    "applies_to": ["Hit"],  # Hit 데미지만
    "not_applies_to": ["DoT", "Secondary", "Reflection", "True"],
    "stacking": "additive",  # 확률은 합산
    "description": "Hit 시 일정 확률로 2배 피해",
    "recommended_for": [
        "Hit Damage builds",
        "High damage per hit builds"
    ]
}


# ==============================================================================
# 스킬 속도 (Skill Speed)
# ==============================================================================

SKILL_SPEED = {
    "Attack Speed": {
        "applies_to": ["Attack Skills"],
        "formula": "Final Speed = Base × (1 + non-add%) × (1 + add%₁) × ...",
        "description": "공격 스킬의 시전 속도",
        "recommended_for": ["Melee", "Bow", "Physical Attack builds"]
    },
    "Cast Speed": {
        "applies_to": ["Spell Skills"],
        "formula": "Final Speed = Base × (1 + non-add%) × (1 + add%₁) × ...",
        "description": "주문 스킬의 시전 속도",
        "recommended_for": ["Spell", "Elemental", "Magic builds"]
    }
}


# ==============================================================================
# 쿨다운 (Cooldown)
# ==============================================================================

COOLDOWN = {
    "formula": "Cooldown = Base / ((1 + non-add%) × (1 + add%₁) × ...)",
    "reduction_stat": "Cooldown Recovery Speed",
    "description": "회복 속도가 빠를수록 쿨다운 감소",
    "recommended_for": [
        "Skills with high cooldown",
        "Burst damage builds"
    ]
}


# ==============================================================================
# 스킬 태그별 추천 스탯 (Skill Tags Synergy)
# ==============================================================================

SKILL_TAG_SYNERGIES = {
    "DoT": {
        "recommended_stats": ["Affliction", "Reaping", "Duration", "Ailment Chance"],
        "damage_form": "DoT",
        "avoid_stats": ["Critical Strike", "Double Damage", "Accuracy"]
    },
    "AoE": {
        "recommended_stats": ["Area Damage", "Area of Effect", "Explosion Damage"],
        "synergies": ["Secondary Damage", "Chain"]
    },
    "Melee": {
        "recommended_stats": ["Attack Speed", "Physical Damage", "Melee Range"],
        "skill_speed_type": "Attack Speed",
        "typical_damage_types": ["Physical"]
    },
    "Spell": {
        "recommended_stats": ["Cast Speed", "Spell Damage", "Mana", "Mana Regeneration"],
        "skill_speed_type": "Cast Speed",
        "typical_damage_types": ["Fire", "Cold", "Lightning"]
    },
    "Projectile": {
        "recommended_stats": ["Projectile Speed", "Pierce", "Chain", "Fork"],
        "synergies": ["Multiple Projectiles"]
    },
    "Attack": {
        "recommended_stats": ["Attack Speed", "Accuracy", "Attack Damage"],
        "skill_speed_type": "Attack Speed"
    },
    "Channeled": {
        "recommended_stats": ["Mana Cost Reduction", "Mana Regeneration", "Duration"],
        "special": "지속 시전 스킬"
    },
    "Summon": {
        "recommended_stats": ["Minion Damage", "Minion Life", "Maximum Summons"],
        "build_type": "Summoner/Pet build"
    },
    "Curse": {
        "recommended_stats": ["Curse Effect", "Curse Duration", "Area of Effect"],
        "build_type": "Support/Debuff build"
    },
    "Warcry": {
        "recommended_stats": ["Warcry Effect", "Cooldown Recovery", "Area of Effect"],
        "build_type": "Buff build"
    }
}


# ==============================================================================
# 스탯 효과 (Stat Effects)
# ==============================================================================

STAT_EFFECTS = {
    "STR": {
        "primary_for": ["Berserker", "Warrior", "Commander"],
        "typical_bonuses": ["Physical Damage", "Life", "Armor"],
        "playstyle": "Melee, Tank, Physical damage"
    },
    "DEX": {
        "primary_for": ["Ranger", "Spacetime Witness", "Carino", "Divineshot"],
        "typical_bonuses": ["Attack Speed", "Evasion", "Accuracy", "Projectile Damage"],
        "playstyle": "Ranged, Agile, Attack-based"
    },
    "INT": {
        "primary_for": ["Mage", "Oracle"],
        "typical_bonuses": ["Spell Damage", "Mana", "Energy Shield"],
        "playstyle": "Spellcaster, Elemental damage"
    }
}


# ==============================================================================
# 빌드 추천을 위한 유틸리티 함수
# ==============================================================================

def get_recommended_stats_for_damage_form(damage_form: str) -> list:
    """데미지 형태에 맞는 추천 스탯 반환"""
    return DAMAGE_FORMS.get(damage_form, {}).get("recommended_stats", [])


def get_recommended_stats_for_skill_tags(tags: list) -> list:
    """스킬 태그들에 맞는 추천 스탯 반환"""
    recommended = []
    for tag in tags:
        tag_synergies = SKILL_TAG_SYNERGIES.get(tag, {})
        recommended.extend(tag_synergies.get("recommended_stats", []))
    return list(set(recommended))  # 중복 제거


def should_avoid_crit_for_skill(tags: list) -> bool:
    """스킬이 크리티컬을 피해야 하는지 판단"""
    # DoT 스킬은 크리티컬 불필요
    return "DoT" in tags


def get_skill_speed_type(tags: list) -> str:
    """스킬에 맞는 속도 타입 반환 (Attack Speed / Cast Speed)"""
    if "Spell" in tags:
        return "Cast Speed"
    elif "Attack" in tags or "Melee" in tags:
        return "Attack Speed"
    return "Unknown"


def get_primary_stat_for_god_type(god_type: str) -> str:
    """God 타입에 맞는 주 스탯 반환"""
    for stat, info in STAT_EFFECTS.items():
        if god_type in info.get("primary_for", []):
            return stat
    return "STR"  # 기본값


def can_convert_damage_type(from_type: str, to_type: str) -> bool:
    """데미지 타입 변환 가능 여부 확인"""
    try:
        from_priority = DAMAGE_TYPES[from_type]["conversion_priority"]
        to_priority = DAMAGE_TYPES[to_type]["conversion_priority"]
        return from_priority < to_priority  # 낮은 우선순위 → 높은 우선순위만 가능
    except KeyError:
        return False


# ==============================================================================
# 빌드 아키타입 (Build Archetypes)
# ==============================================================================

BUILD_ARCHETYPES = {
    "Physical Melee": {
        "damage_types": ["Physical"],
        "damage_forms": ["Hit"],
        "skill_tags": ["Melee", "Attack"],
        "recommended_stats": ["Attack Speed", "Physical Damage", "Accuracy", "Crit"],
        "primary_stat": "STR"
    },
    "Elemental Spell": {
        "damage_types": ["Fire", "Cold", "Lightning"],
        "damage_forms": ["Hit"],
        "skill_tags": ["Spell"],
        "recommended_stats": ["Cast Speed", "Spell Damage", "Elemental Damage", "Crit"],
        "primary_stat": "INT"
    },
    "DoT / Ailment": {
        "damage_types": ["Fire", "Cold", "Erosion"],
        "damage_forms": ["DoT"],
        "skill_tags": ["DoT", "Spell"],
        "recommended_stats": ["Affliction", "Reaping", "Duration", "Ailment Chance"],
        "avoid_stats": ["Crit", "Double Damage"],
        "primary_stat": "INT"
    },
    "Bow / Projectile": {
        "damage_types": ["Physical", "Lightning"],
        "damage_forms": ["Hit"],
        "skill_tags": ["Projectile", "Attack"],
        "recommended_stats": ["Attack Speed", "Projectile Speed", "Pierce", "Crit"],
        "primary_stat": "DEX"
    },
    "Summoner": {
        "skill_tags": ["Summon"],
        "recommended_stats": ["Minion Damage", "Minion Life", "Maximum Summons"],
        "primary_stat": "INT"
    }
}


# ==============================================================================
# 상태이상 (Ailments) - 상세 정보
# ==============================================================================

AILMENTS = {
    "Ignite": {
        "damage_type": "Fire",
        "damage_form": "DoT",
        "duration": 4.0,  # seconds
        "default_stacks": 1,
        "can_stack": True,  # 장비로 증가 가능
        "base_damage_source": "Base Ignite Damage",
        "default_bonus": "+30% Affliction effect",
        "description": "화염 지속 피해, 4초 동안 매초 피해",
        "scaling_stats": [
            "Fire Damage",
            "Damage Over Time",
            "Affliction",
            "Ignite Damage",
            "Base Ignite Damage"
        ],
        "build_synergies": [
            "Fire Damage Over Time builds",
            "Affliction-focused builds",
            "Hybrid Fire Hit + DoT builds"
        ]
    },
    "Shock": {
        "damage_type": "Lightning",
        "damage_form": "Secondary",
        "duration": 4.0,
        "default_stacks": 1,
        "can_stack": False,  # 항상 1개 (변경 불가)
        "base_damage_calculation": "3% of Lightning Damage hit",
        "trigger_limit": 12,  # 최대 12회 트리거
        "trigger_on": "Hit on Shocked enemy",
        "ignores_resistance": True,
        "description": "번개 2차 피해, 저항 무시, 피격 시마다 트리거 (최대 12회)",
        "scaling_stats": [
            "Lightning Damage",
            "Shock Damage",
            "Hit Frequency"  # 자주 때릴수록 좋음
        ],
        "build_synergies": [
            "Fast-hitting Lightning builds",
            "Multi-hit skills",
            "Attack Speed builds"
        ]
    },
    "Trauma": {
        "damage_type": "Physical",
        "damage_form": "DoT",
        "duration": 4.0,
        "default_stacks": 1,
        "can_stack": False,  # 가장 높은 피해만 적용
        "base_damage_source": "Base Trauma Damage",
        "default_bonus": "+30% Reaping Duration",
        "description": "물리 지속 피해, 4초 동안 매초 피해",
        "scaling_stats": [
            "Physical Damage",
            "Damage Over Time",
            "Reaping",
            "Trauma Damage",
            "Base Trauma Damage"
        ],
        "build_synergies": [
            "Physical DoT builds",
            "Reaping-focused builds",
            "Bleed builds"
        ]
    },
    "Wilt": {
        "damage_type": "Erosion",
        "damage_form": "DoT",
        "duration": 1.0,  # 가장 짧은 지속시간!
        "default_stacks": float('inf'),  # 무한 스택!
        "can_stack": True,
        "stacking_behavior": "독립적 (각 스택이 독립적으로 피해)",
        "base_damage_source": "Base Wilt Damage",
        "description": "부식 지속 피해, 1초마다, 무한 스택 가능 (유일!)",
        "scaling_stats": [
            "Erosion Damage",
            "Damage Over Time",
            "Wilt Damage",
            "Base Wilt Damage",
            "Wilt Stack Count"  # 스택 수에 따라 추가 보너스
        ],
        "build_synergies": [
            "Erosion DoT builds",
            "Stack-scaling builds",
            "High application rate builds"
        ],
        "unique_mechanic": "스택당 Erosion Damage 증가 (최대 60스택)"
    },
    "Numbed": {
        "damage_type": "Lightning",
        "damage_form": "Debuff",  # 피해 아님, 디버프
        "duration": 2.0,  # per stack
        "default_stacks": 1,
        "max_stacks": 10,
        "effect_per_stack": "+5% damage taken",
        "max_effect": "+50% damage taken (10 stacks)",
        "stacking_condition": "Lightning Damage hits / 10% of (Life + ES) dealt",
        "description": "번개 디버프, 스택당 +5% 받는 피해 증가 (최대 10스택)",
        "scaling_stats": [
            "Lightning Damage",
            "Numbed Chance",
            "Numbed Duration",
            "Numbed Effect"
        ],
        "build_synergies": [
            "Lightning damage builds",
            "High damage per hit builds",
            "Debuff-focused builds"
        ],
        "special_interaction": "Numbed 적에게 추가 효과 (특정 장비/재능)"
    },
    "Frostbite/Freeze": {
        "damage_type": "Cold",
        "damage_form": "Control",  # 군중 제어
        "duration": 4.0,
        "frostbite_effect": "Slow (이동 속도 감소)",
        "freeze_effect": "Immobilize (이동 불가, 일반 몬스터) + Reduced Damage",
        "boss_behavior": "레전더리 보스는 완전 빙결 불가",
        "description": "냉기 군중 제어, 이동 속도 감소 / 빙결",
        "scaling_stats": [
            "Cold Damage",
            "Freeze Chance",
            "Freeze Duration",
            "Ailment Chance"
        ],
        "build_synergies": [
            "Cold damage builds",
            "Control/defensive builds",
            "Shatter builds (frozen enemy kill effects)"
        ]
    }
}


# ==============================================================================
# 스킬 메커니즘: Spell Burst
# ==============================================================================

SPELL_BURST = {
    "introduced": "Season 3",
    "applies_to": ["Spell Skills"],
    "excluded_skills": [
        "Skills with Cooldown",
        "Summon Skills",
        "Sentry Skills",
        "Channeled Skills"
    ],
    "mechanic": "충전 완료 시 스킬을 여러 번 시전",
    "cast_count": "Consumed stacks",  # 소비한 스택 수만큼 시전
    "charge_time": 2.0,  # seconds (기본)
    "min_stacks_required": 1,
    "scaling_stats": [
        "Spell Burst Charge Speed",
        "Max Spell Burst",
        "Cast Speed"  # 여러 번 시전하므로 Cast Speed도 중요
    ],
    "recommended_for": [
        "Spell builds",
        "High damage per cast skills",
        "Non-cooldown spells"
    ],
    "not_compatible_with": [
        "Combo skills",
        "Cooldown skills",
        "Summon/Sentry"
    ]
}


# ==============================================================================
# 스킬 메커니즘: Combo
# ==============================================================================

COMBO = {
    "structure": "2 Starters + 1 Finisher",
    "combo_points": {
        "generation": "1 point per Starter cast",
        "consumption": "Finisher consumes all points"
    },
    "damage_formula": "Base Damage × (1 + Combo Points × Combo Finisher Amplification)",
    "sequence_window": 1.5,  # seconds
    "reset_conditions": [
        "Using Non-Instant, Non-Mobility skills",
        "Triggering other Combo skills",
        "1.5 second timeout"
    ],
    "allowed_during_combo": [
        "Mobility skills (Blink, etc.)",
        "Instant skills"
    ],
    "scaling_stats": [
        "Combo Damage",
        "Combo Finisher Amplification",
        "Combo Starter/Finisher charges"
    ],
    "recommended_for": [
        "Melee builds",
        "Burst damage builds",
        "Skill rotation playstyles"
    ],
    "not_compatible_with": [
        "Spell Burst"
    ],
    "build_tip": "콤보 포인트는 곱셈 스케일링 → 높은 증폭값이 핵심"
}


# ==============================================================================
# 빌드 추천을 위한 고급 유틸리티 함수
# ==============================================================================

def get_ailment_for_damage_type(damage_type: str) -> str:
    """데미지 타입에 해당하는 상태이상 반환"""
    return DAMAGE_TYPES.get(damage_type, {}).get("ailment", "Unknown")


def get_ailment_info(ailment_name: str) -> dict:
    """상태이상 상세 정보 반환"""
    return AILMENTS.get(ailment_name, {})


def should_focus_on_stacking(ailment_name: str) -> bool:
    """스택 쌓기가 중요한 상태이상인지 판단"""
    ailment = AILMENTS.get(ailment_name, {})
    # Wilt는 무한 스택, Numbed는 최대 10스택
    return ailment.get("default_stacks", 1) > 1 or ailment.get("max_stacks", 1) > 1


def is_dot_ailment(ailment_name: str) -> bool:
    """DoT 형태의 상태이상인지 판단"""
    ailment = AILMENTS.get(ailment_name, {})
    return ailment.get("damage_form") == "DoT"


def get_recommended_stats_for_ailment(ailment_name: str) -> list:
    """상태이상에 맞는 추천 스탯 반환"""
    ailment = AILMENTS.get(ailment_name, {})
    return ailment.get("scaling_stats", [])


def is_spell_burst_compatible(skill_tags: list) -> bool:
    """Spell Burst와 호환되는 스킬인지 판단"""
    if "Spell" not in skill_tags:
        return False

    excluded = ["Cooldown", "Summon", "Sentry", "Channeled", "Combo"]
    for tag in excluded:
        if tag in skill_tags:
            return False

    return True


def is_combo_skill(skill_tags: list) -> bool:
    """Combo 스킬인지 판단"""
    return "Combo" in skill_tags


if __name__ == "__main__":
    # 테스트
    print("=== Torchlight Infinite 게임 메커니즘 참조 데이터 ===\n")

    print("1. 데미지 타입:")
    for dtype, info in DAMAGE_TYPES.items():
        print(f"   {dtype}: {info['ailment']} (저항 무시: {info.get('bypasses_resistance', False)})")

    print("\n2. 데미지 형태:")
    for dform, info in DAMAGE_FORMS.items():
        print(f"   {dform}: {info['description']}")

    print("\n3. 상태이상 (Ailments):")
    for ailment_name, ailment_info in AILMENTS.items():
        stacks = ailment_info.get('max_stacks') or ailment_info.get('default_stacks', 1)
        print(f"   {ailment_name}: {ailment_info['damage_type']} - {ailment_info['description'][:50]}... (최대 스택: {stacks})")

    print("\n4. 유틸리티 함수 테스트:")
    print(f"   DoT 스킬은 크리티컬 피해야? {should_avoid_crit_for_skill(['DoT'])}")
    print(f"   Spell 태그 → 속도 타입: {get_skill_speed_type(['Spell'])}")
    print(f"   Berserker → 주 스탯: {get_primary_stat_for_god_type('Berserker')}")
    print(f"   Physical → Fire 변환 가능? {can_convert_damage_type('Physical', 'Fire')}")
    print(f"   Fire → Physical 변환 가능? {can_convert_damage_type('Fire', 'Physical')}")
    print(f"   Wilt는 스택 쌓기 중요? {should_focus_on_stacking('Wilt')}")
    print(f"   Ignite는 DoT 상태이상? {is_dot_ailment('Ignite')}")
    print(f"   Spell (no cooldown) → Spell Burst 가능? {is_spell_burst_compatible(['Spell'])}")
    print(f"   Spell + Cooldown → Spell Burst 가능? {is_spell_burst_compatible(['Spell', 'Cooldown'])}")
