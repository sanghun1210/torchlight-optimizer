"""
AI Recommendation Service - OpenAI API 연동
"""
import os
import json
from typing import Dict, Optional
from openai import OpenAI

from backend.recommendation.context_builder import ContextBuilder


class AIRecommendationService:
    """OpenAI API 기반 빌드 추천 서비스"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: OpenAI API 키 (None이면 환경변수에서 로드)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # 기본 모델

    def generate_build_recommendation(
        self,
        context: Dict,
        max_skills: int = 6,
        max_items: int = 10
    ) -> Dict:
        """
        AI 기반 빌드 추천 생성

        Args:
            context: ContextBuilder.build_hero_context()의 반환값
            max_skills: 추천할 최대 스킬 개수
            max_items: 추천할 최대 아이템 개수

        Returns:
            구조화된 빌드 추천
        """
        # 1. 컨텍스트를 프롬프트로 변환
        context_builder = ContextBuilder(db=None)  # format only
        context_text = context_builder.format_context_for_prompt(context)

        # 2. 시스템 프롬프트 생성
        system_prompt = self._build_system_prompt()

        # 3. 사용자 프롬프트 생성
        user_prompt = self._build_user_prompt(
            context_text,
            max_skills,
            max_items
        )

        # 4. OpenAI API 호출
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}  # JSON 모드 활성화
            )

            # 5. 응답 파싱
            response_text = response.choices[0].message.content
            recommendation = json.loads(response_text)

            # 6. 메타데이터 추가
            recommendation["ai_metadata"] = {
                "model": self.model,
                "tokens_used": response.usage.total_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens
            }

            return recommendation

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {e}")

    def _build_system_prompt(self) -> str:
        """시스템 프롬프트 생성 - AI의 역할 정의"""
        return """You are an expert Torchlight Infinite build theorycrafter with deep knowledge of game mechanics.

# GAME MECHANICS KNOWLEDGE

## Damage Formula
Final Damage = Base Damage × (1 + Σ Additive Bonuses) × Π Multiplicative Bonuses
- Additive bonuses (+x% increased damage) sum together
- Multiplicative bonuses (x% additional damage) multiply separately - MORE VALUABLE!

## Damage Types & Ailments
- **Physical** → Trauma (DoT, needs Reaping)
- **Fire** → Ignite (single stack, needs high single-hit damage + Affliction)
- **Cold** → Frostbite/Freeze (control)
- **Lightning** → Shock (secondary damage on hit)
- **Erosion** → Wilt (infinite stacks, needs high attack speed + Affliction)

## Critical Strike
- ONLY works on Hits (NOT on DoT/Ailments)
- If build is DoT-focused, crit is LESS valuable
- If build is Hit-focused, crit is ESSENTIAL

## Ailment Mechanics
- **Ignite**: Single stack (doesn't stack). Needs BIGGEST hit possible + Affliction scaling
- **Wilt**: Infinite stacks. Needs FAST attack speed to stack quickly + Affliction
- **Trauma**: Physical DoT. Synergizes with Reaping (instant damage)
- **Shock**: Lightning secondary damage. Good for fast-hitting builds

## Skill Synergies
- **Spell Burst**: Low cooldown spells → instant multi-cast burst
- **Multistrike**: Melee/Attacks → free extra attacks with +20% damage
- **Combo**: Starter skill → Finisher skill (consumes points for huge bonus)
- **Channeled**: Stacks over time. Vulnerable but powerful
- **Chain**: Projectiles jump. Excellent for pack clearing

## Key Build Synergies
1. **Ignite Build**: High single-hit damage + Affliction + Reaping + avoid attack speed
2. **Wilt Build**: High attack speed + Affliction + Reaping + Erosion damage
3. **Physical DoT**: Trauma + Reaping + Affliction + avoid crit
4. **Hit-Based**: Critical Strike + Critical Damage + Multistrike
5. **Spell Burst**: Low cooldown spells + spell damage + burst mechanics

# CRITICAL RULES
1. **NO HALLUCINATIONS**: Only recommend skills/items from the provided context
2. **DATA INTEGRITY**: Use exact names from database
3. **MECHANICS-AWARE**: Apply the game mechanics knowledge above
4. **SYNERGY FOCUS**: Prioritize multiplicative bonuses and mechanic synergies
5. **BUILD COHERENCE**: Clear focus (DoT vs Hit, which damage type)

OUTPUT FORMAT:
Return a JSON object with the following structure:
{
  "hero_name": "string",
  "talent_name": "string",
  "build_type": "DoT | Hit | Hybrid | Burst",
  "build_summary": "1-2 sentence description",
  "recommended_skills": [
    {
      "skill_name": "exact name from context",
      "skill_id": integer,
      "priority": 1-5,
      "reason": "why this skill synergizes"
    }
  ],
  "recommended_items": [
    {
      "item_name": "exact name from context",
      "item_id": integer,
      "slot": "string",
      "reason": "why this item synergizes"
    }
  ],
  "synergy_explanation": "Detailed explanation of how talent, skills, and items work together",
  "playstyle_tips": ["tip1", "tip2", "tip3"]
}

Remember: Accuracy over creativity. Only use data from the provided context."""

    def _build_user_prompt(
        self,
        context_text: str,
        max_skills: int,
        max_items: int
    ) -> str:
        """사용자 프롬프트 생성"""
        user_preferences = ""

        prompt = f"""Based on the following game data, create an optimal build recommendation.

{context_text}

TASK:
1. Analyze the talent mechanics carefully (especially high-level effects)
2. Select up to {max_skills} skills that best synergize with the talent
3. Select up to {max_items} items that amplify the build's strengths
4. Explain the synergies clearly

CONSTRAINTS:
- Recommend ONLY skills and items listed in the context above
- Use exact names as they appear in the context
- Prioritize synergies with talent mechanics
- Ensure build coherence (don't mix conflicting mechanics)

Return your recommendation as a JSON object following the specified format."""

        return prompt

    async def generate_build_recommendation_async(
        self,
        context: Dict,
        max_skills: int = 6,
        max_items: int = 10
    ) -> Dict:
        """
        비동기 버전의 빌드 추천 생성 (향후 FastAPI async 엔드포인트용)

        현재는 동기 함수를 래핑한 형태
        """
        # 실제 비동기 구현을 위해서는 asyncio.to_thread 또는 httpx 사용 필요
        import asyncio
        return await asyncio.to_thread(
            self.generate_build_recommendation,
            context,
            max_skills,
            max_items
        )
