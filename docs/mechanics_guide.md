# Torchlight Infinite: Game Mechanics Handbook

This document summarizes core game mechanics, damage formulas, and skill interactions. It serves as a knowledge base for the AI recommendation engine to provide accurate, mechanics-aware advice.

## 1. Damage Mechanics

### 1.1 Damage Types
There are 5 fundamental damage types.
- **Physical:** Default type. Mitigated by Armor and Physical Resistance.
- **Fire:** Elemental. Mitigated by Fire Resistance. Associated with **Ignite**.
- **Cold:** Elemental. Mitigated by Cold Resistance. Associated with **Frostbite/Freeze**.
- **Lightning:** Elemental. Mitigated by Lightning Resistance. Associated with **Shock**.
- **Erosion:** Chaos-like. Mitigated by Erosion Resistance. Associated with **Wilt**.

### 1.2 Calculation Formula
Damage is calculated as:
`Final Damage = Base Damage * (1 + Sum of Additive Bonuses) * (Product of Multiplicative Bonuses)`

- **Base Damage:** Comes from Weapon or Skill base values.
- **Additive Bonuses (`+x% increased damage`):** All sources sum up before multiplying.
- **Multiplicative Bonuses (`x% additional damage`):** Each source multiplies independently. *This is usually more valuable than increased damage.*

### 1.3 Critical Strike
- Applies to **Hits** only (not DoT).
- **Crit Chance:** Determined by Critical Strike Rating.
- **Crit Damage:** Defaults to 150% (1.5x) of normal damage. Can be increased by "Critical Strike Damage" stat.

## 2. Ailments & Damage Over Time (DoT)

Ailments are negative effects applied by Hits.
**Important:** Ailment Damage is calculated separately from Hit Damage. It requires a non-zero "Base Ailment Damage" (usually % of Weapon/Skill damage).

### 2.1 Damage Ailments
| Ailment | Type | Duration (Base) | Stack Limit | Key Mechanic |
| :--- | :--- | :--- | :--- | :--- |
| **Ignite** | Fire DoT | 4s | 1 | Does not stack by default. Only highest damage applies. Benefits from "Affliction". |
| **Wilt** | Erosion DoT | 1s | Infinite | Stacks infinitely. Good for high attack speed. |
| **Trauma** | Physical DoT | 4s | 1 | Adds "Reaping Duration". Does not stack by default. |
| **Shock** | Lightning | 4s | 1 | Deals Secondary Lightning Damage when enemy is hit (up to 12 times). Ignores resistance. |

### 2.2 Control Ailments
- **Frostbite/Freeze:** Reduces speed. At 100 Rating, target freezes (immobilized, -20% dmg dealt).
- **Numbed:** Increases damage taken.

### 2.3 Advanced Mechanics
- **Affliction:** Increases DoT taken by enemies. 1 Affliction Rating = +1% DoT taken.
- **Reaping:** Instantly deals a portion of remaining DoT damage. Like "fast-forwarding" the damage.

## 3. Skill Mechanics

### 3.1 Skill Types
- **Active:** Manually used.
- **Support:** Links to Active/Passive skills to enhance them. Multiplies Mana Cost.
- **Passive:** Always active or triggered. Reserves Mana (Sealed Mana).

### 3.2 Special Mechanics
- **Spell Burst (Spells):** Stores charges to cast a spell multiple times instantly. Good for burst damage.
- **Multistrike (Attacks):** Chance to attack again automatically. Gained attacks have +20% speed and damage increments.
- **Channeled:** Continuous cast. Gains "stacks" over time. Vulnerable while standing still.
- **Chain:** Projectiles jump between enemies. Good for clearing packs.
- **Combo:** Sequence of skills (Starter -> Finisher). Finisher consumes points for big bonuses.

## 4. Synergy Guidelines for AI
- **Ignite Builds:** Prioritize high single-hit damage (to maximize the one Ignite stack) and "Affliction".
- **Wilt Builds:** Prioritize high hit rate/attack speed to stack Wilt infinitely.
- **Spell Burst:** Best for Spells with low cooldown or no cooldown.
- **Multistrike:** Essential for most Melee/Attack builds for free extra damage.
- **Reaping:** Mandatory for maximizing DoT DPS (Trauma/Ignite) to bypass wait times.
