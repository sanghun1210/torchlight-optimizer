"""
영웅 재능(Talent) 메커니즘 참조 데이터

각 재능의 핵심 메커니즘과 빌드 방향성을 정의
"""

TALENT_MECHANICS = {
    "Anger": {
        "hero": "Rehan",
        "god_type": "Berserker",
        "core_mechanic": "Burst Damage",
        "description": "Burst 피해에 완전히 특화. 60레벨에 일반 스킬 -80% 페널티",
        "key_features": {
            "rage_generation": "Melee Attack으로 Rage 생성",
            "burst_trigger": "공격 시 Burst 트리거 (0.3초 쿨다운)",
            "tunnel_vision": "-80% damage for non-Burst skills (Lv60)",
            "burst_bonus": "+66~110% additional Burst Damage",
            "attack_speed_synergy": "Attack Speed = Burst Cooldown Recovery",
            "area_synergy": "Area +2% → Burst Damage +1% (최대 +90%)",
            "crit_synergy": "Burst Crit → Rage 생성"
        },
        "build_focus": "Burst",
        "must_have_mechanics": [
            "Melee Attack",  # Rage 생성
            "Attack Speed",  # Burst 쿨다운 감소
            "Critical Strike",  # Rage 생성
            "Area"  # Burst 피해 증가
        ],
        "avoid_mechanics": [
            "Non-Burst Damage",  # -80% 페널티
            "DoT",  # Burst와 무관
            "Spell"  # Melee Attack이 아님
        ],
        "recommended_skill_types": [
            "Melee",
            "Attack",
            "AoE"
        ],
        "recommended_item_stats": [
            "Attack Speed",
            "Critical Strike",
            "Area of Effect",
            "Melee Damage",
            "Physical Damage",
            "Rage Generation",
            "Cooldown Recovery"
        ],
        "playstyle": "Melee Burst"
    },

    "Seething Silhouette": {
        "hero": "Rehan",
        "god_type": "Berserker",
        "core_mechanic": "Shadow Clone",
        "description": "그림자 분신을 소환하여 함께 공격",
        "key_features": {
            "shadow_clone": "그림자 분신 소환",
            "clone_damage": "분신도 함께 공격",
            "clone_mechanics": "특정 스킬이 분신도 시전"
        },
        "build_focus": "Hit",
        "must_have_mechanics": [
            "Melee Attack",
            "Attack Speed",
            "Minion Damage"  # 분신 피해 증가
        ],
        "recommended_skill_types": [
            "Melee",
            "Attack"
        ],
        "recommended_item_stats": [
            "Attack Speed",
            "Melee Damage",
            "Minion Damage",
            "Physical Damage"
        ],
        "playstyle": "Melee Clone"
    },

    # 다른 재능들도 추가 가능
    "Ranger of Glory": {
        "hero": "Carino",
        "god_type": "Divineshot",
        "core_mechanic": "Projectile",
        "build_focus": "Hit",
        "must_have_mechanics": [
            "Projectile",
            "Attack Speed",
            "Pierce"
        ],
        "recommended_skill_types": [
            "Projectile",
            "Attack",
            "Bow"
        ],
        "recommended_item_stats": [
            "Projectile Speed",
            "Attack Speed",
            "Pierce",
            "Projectile Damage"
        ],
        "playstyle": "Ranged Projectile"
    },
}


def get_talent_mechanics(talent_name: str) -> dict:
    """재능의 메커니즘 정보 반환"""
    return TALENT_MECHANICS.get(talent_name, {})


def get_talent_build_focus(talent_name: str) -> str:
    """재능의 빌드 초점 반환 (Burst/Hit/DoT/Hybrid)"""
    mechanics = get_talent_mechanics(talent_name)
    return mechanics.get("build_focus", "Hit")


def get_talent_must_have_mechanics(talent_name: str) -> list:
    """재능에 필수적인 메커니즘 목록"""
    mechanics = get_talent_mechanics(talent_name)
    return mechanics.get("must_have_mechanics", [])


def get_talent_avoid_mechanics(talent_name: str) -> list:
    """재능에서 피해야 할 메커니즘 목록"""
    mechanics = get_talent_mechanics(talent_name)
    return mechanics.get("avoid_mechanics", [])


def get_recommended_skill_types(talent_name: str) -> list:
    """재능에 추천되는 스킬 타입"""
    mechanics = get_talent_mechanics(talent_name)
    return mechanics.get("recommended_skill_types", [])


def get_recommended_item_stats(talent_name: str) -> list:
    """재능에 추천되는 아이템 스탯"""
    mechanics = get_talent_mechanics(talent_name)
    return mechanics.get("recommended_item_stats", [])


def is_burst_focused_talent(talent_name: str) -> bool:
    """Burst 중심 재능인지 판단"""
    mechanics = get_talent_mechanics(talent_name)
    return mechanics.get("core_mechanic") == "Burst Damage"


def get_talent_playstyle(talent_name: str) -> str:
    """재능의 플레이스타일"""
    mechanics = get_talent_mechanics(talent_name)
    return mechanics.get("playstyle", "Unknown")


if __name__ == "__main__":
    # 테스트
    print("=== 재능 메커니즘 참조 데이터 ===\n")

    talent = "Anger"
    print(f"재능: {talent}")
    mechanics = get_talent_mechanics(talent)

    print(f"\n핵심 메커니즘: {mechanics.get('core_mechanic')}")
    print(f"설명: {mechanics.get('description')}")
    print(f"\n빌드 초점: {get_talent_build_focus(talent)}")
    print(f"Burst 중심? {is_burst_focused_talent(talent)}")

    print(f"\n필수 메커니즘:")
    for mech in get_talent_must_have_mechanics(talent):
        print(f"  ✅ {mech}")

    print(f"\n피해야 할 메커니즘:")
    for mech in get_talent_avoid_mechanics(talent):
        print(f"  ❌ {mech}")

    print(f"\n추천 스킬 타입:")
    for skill_type in get_recommended_skill_types(talent):
        print(f"  - {skill_type}")

    print(f"\n추천 아이템 스탯:")
    for stat in get_recommended_item_stats(talent):
        print(f"  - {stat}")
