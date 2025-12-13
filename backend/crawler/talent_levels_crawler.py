"""
재능 레벨 효과(Talent Levels) 크롤러
각 재능의 레벨별 효과를 크롤링
"""
import json
import logging
import re
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from backend.crawler.base_crawler import BaseCrawler
from backend.database.models import TalentLevel
from backend.database.db import get_db_session

logger = logging.getLogger(__name__)


class TalentLevelsCrawler(BaseCrawler):
    """재능 레벨 효과 크롤러"""

    # 19개 재능 URL 목록
    TALENT_URLS = [
        "https://tlidb.com/en/Anger",
        "https://tlidb.com/en/Seething_Silhouette",
        "https://tlidb.com/en/Ranger_of_Glory",
        "https://tlidb.com/en/Lethal_Flash",
        "https://tlidb.com/en/Zealot_of_War",
        "https://tlidb.com/en/Wind_Stalker",
        "https://tlidb.com/en/Lightning_Shadow",
        "https://tlidb.com/en/Blast_Nova",
        "https://tlidb.com/en/Creative_Genius",
        "https://tlidb.com/en/Flame_of_Pleasure",
        "https://tlidb.com/en/Frostbitten_Heart",
        "https://tlidb.com/en/Ice-Fire_Fusion",
        "https://tlidb.com/en/Wisdom_of_The_Gods",
        "https://tlidb.com/en/Incarnation_of_the_Gods",
        "https://tlidb.com/en/Spacetime_Elapse",
        "https://tlidb.com/en/High_Court_Chariot",
        "https://tlidb.com/en/Unsullied_Blade",
        "https://tlidb.com/en/Growing_Breeze",
        "https://tlidb.com/en/Sing_with_the_Tide",
    ]

    def crawl_all_talent_levels(self) -> List[Dict]:
        """
        모든 재능의 레벨별 효과 크롤링

        Returns:
            재능 레벨 정보 딕셔너리 리스트
        """
        all_talent_levels = []

        for url in self.TALENT_URLS:
            talent_name = url.split('/')[-1].replace('_', ' ')
            logger.info(f"Crawling talent: {talent_name}")

            talent_levels = self._crawl_talent_page(url, talent_name)
            all_talent_levels.extend(talent_levels)

            logger.info(f"Found {len(talent_levels)} level effects for {talent_name}")

        logger.info(f"Total talent level effects collected: {len(all_talent_levels)}")
        return all_talent_levels

    def _crawl_talent_page(self, url: str, talent_name: str) -> List[Dict]:
        """
        개별 재능 페이지 크롤링

        Args:
            url: 재능 페이지 URL
            talent_name: 재능 이름

        Returns:
            레벨 효과 리스트
        """
        soup = self.fetch_page(url)
        if not soup:
            logger.error(f"Failed to fetch talent page: {url}")
            return []

        talent_levels = []

        try:
            # 구조:
            # <div class="row row-cols-1 row-cols-lg-2 g-2">
            #   <div class="col">
            #     <div class="d-flex border-top rounded">
            #       <div class="flex-shrink-0"><img></div>
            #       <div class="flex-grow-1 mx-2 my-1">
            #         <div class="fw-bold">Effect Name</div>
            #         Require lv X
            #         <hr>
            #         <div>Description...</div>
            #       </div>
            #     </div>
            #   </div>
            # </div>

            # 모든 flex-grow-1 컨테이너 찾기
            talent_containers = soup.find_all('div', class_='flex-grow-1')

            for container in talent_containers:
                # mx-2와 my-1 클래스가 있는지 확인 (재능 효과 컨테이너)
                if 'mx-2' not in container.get('class', []) or 'my-1' not in container.get('class', []):
                    continue

                # 효과 이름 (fw-bold div)
                name_div = container.find('div', class_='fw-bold')
                if not name_div:
                    continue

                effect_name = self.extract_text(name_div).strip()
                if not effect_name or len(effect_name) < 2:
                    continue

                # "Require lv X" 텍스트 노드 찾기
                level = None
                for content in container.strings:
                    content_str = str(content).strip()
                    level_match = re.search(r'Require\s+lv\s+(\d+)', content_str, re.IGNORECASE)
                    if level_match:
                        level = int(level_match.group(1))
                        break

                if level is None:
                    logger.debug(f"No level found for effect: {effect_name}")
                    continue

                # 효과 설명 (hr 이후의 div)
                effect_description = ""
                hr = container.find('hr')
                if hr:
                    desc_div = hr.find_next_sibling('div')
                    if desc_div:
                        effect_description = self.extract_text(desc_div).strip()

                # hr이 없거나 설명을 못 찾았으면 마지막 div 사용
                if not effect_description or len(effect_description) < 10:
                    all_divs = container.find_all('div', recursive=False)
                    for div in reversed(all_divs):
                        if 'fw-bold' not in div.get('class', []):
                            text = self.extract_text(div).strip()
                            if len(text) > 10:
                                effect_description = text
                                break

                if not effect_description or len(effect_description) < 10:
                    logger.debug(f"No description found for: {effect_name} (Level {level})")
                    continue

                # 메커니즘 키워드 추출
                mechanics = self._extract_mechanics(effect_description, level)

                talent_levels.append({
                    'talent_name': talent_name,
                    'level': level,
                    'effect_name': effect_name,
                    'effect_description': effect_description[:1000],  # 최대 1000자
                    'mechanics': json.dumps(mechanics)
                })
                logger.debug(f"Found: {talent_name} - {effect_name} (Level {level})")

        except Exception as e:
            logger.error(f"Error parsing talent page {url}: {e}")
            import traceback
            traceback.print_exc()

        return talent_levels

    def _extract_effect_name(self, header, header_text: str) -> str:
        """효과 이름 추출"""
        # "Level X: Effect Name" 패턴
        if ':' in header_text:
            parts = header_text.split(':', 1)
            if len(parts) > 1:
                return parts[1].strip()

        # 헤더 다음의 strong 또는 b 태그에서 찾기
        next_elem = header.find_next(['strong', 'b'])
        if next_elem:
            effect_text = self.extract_text(next_elem).strip()
            # "Level X"가 아닌 경우만
            if not re.match(r'Level\s+\d+', effect_text):
                return effect_text

        # 기본값: 레벨 정보 제거 후 반환
        effect_name = re.sub(r'Level\s+\d+:?\s*', '', header_text, flags=re.IGNORECASE).strip()
        return effect_name if effect_name else "Unnamed Effect"

    def _extract_effect_description(self, header) -> str:
        """효과 설명 추출"""
        # 헤더 다음의 p 태그 또는 다음 형제 요소에서 설명 찾기
        description_parts = []

        # 다음 형제 요소들 탐색
        for sibling in header.find_next_siblings():
            # 다음 헤더를 만나면 중단
            if sibling.name in ['h3', 'h4', 'h5']:
                break

            text = self.extract_text(sibling).strip()
            if text and len(text) > 10:  # 충분히 긴 텍스트만
                description_parts.append(text)

        # 설명이 없으면 부모 요소에서 찾기
        if not description_parts:
            parent = header.parent
            if parent:
                text = self.extract_text(parent).strip()
                # 헤더 텍스트 제거
                header_text = self.extract_text(header).strip()
                text = text.replace(header_text, '').strip()
                if len(text) > 10:
                    description_parts.append(text)

        return ' '.join(description_parts)

    def _extract_mechanics(self, description: str, level: int) -> List[str]:
        """
        효과 설명에서 메커니즘 키워드 추출

        Returns:
            메커니즘 키워드 리스트
        """
        mechanics = []
        desc_lower = description.lower()

        # 주요 메커니즘 키워드 매칭
        mechanic_keywords = {
            'burst': ['burst'],
            'rage': ['rage'],
            'melee': ['melee'],
            'attack_speed': ['attack speed'],
            'critical': ['critical', 'crit'],
            'area': ['area', 'aoe'],
            'damage_penalty': ['-80%', 'damage for non-'],
            'cooldown': ['cooldown'],
            'dot': ['damage over time', 'dot', 'ignite', 'bleed'],
            'spell': ['spell'],
            'projectile': ['projectile'],
            'summon': ['summon', 'minion', 'clone'],
            'affliction': ['affliction', 'ailment'],
        }

        for mech_name, keywords in mechanic_keywords.items():
            if any(kw in desc_lower for kw in keywords):
                mechanics.append(mech_name)

        # 레벨별 중요 메커니즘 태깅
        if level == 60:
            mechanics.append('level_60_critical')  # 60레벨은 보통 중요한 전환점

        return mechanics

    def _parse_text_directly(self, card_bodies, talent_name: str) -> List[Dict]:
        """
        HTML 구조가 명확하지 않을 때 텍스트에서 직접 파싱

        Args:
            card_bodies: card-body 요소들
            talent_name: 재능 이름

        Returns:
            파싱된 레벨 효과 리스트
        """
        talent_levels = []

        for card_body in card_bodies:
            full_text = self.extract_text(card_body)

            # "Level X" 패턴으로 분할
            level_sections = re.split(r'(Level\s+\d+)', full_text)

            for i in range(1, len(level_sections), 2):  # 홀수 인덱스가 "Level X"
                if i + 1 < len(level_sections):
                    level_header = level_sections[i]
                    content = level_sections[i + 1]

                    level_match = re.search(r'Level\s+(\d+)', level_header)
                    if level_match:
                        level = int(level_match.group(1))

                        # 효과 이름: 콜론 이후 또는 첫 줄
                        effect_name = "Level Effect"
                        effect_description = content.strip()

                        # 콜론으로 이름과 설명 분리 시도
                        if ':' in content[:100]:  # 처음 100자 내에서만
                            parts = content.split(':', 1)
                            effect_name = parts[0].strip()
                            effect_description = parts[1].strip() if len(parts) > 1 else content

                        # 메커니즘 추출
                        mechanics = self._extract_mechanics(effect_description, level)

                        if len(effect_description) > 10:  # 충분한 설명이 있을 때만
                            talent_levels.append({
                                'talent_name': talent_name,
                                'level': level,
                                'effect_name': effect_name,
                                'effect_description': effect_description[:500],
                                'mechanics': json.dumps(mechanics)
                            })

        return talent_levels

    def save_talent_levels_to_db(self, talent_levels_data: List[Dict], db: Session):
        """
        크롤링한 재능 레벨 데이터를 데이터베이스에 저장
        """
        saved_count = 0

        for level_data in talent_levels_data:
            try:
                # 기존 데이터 확인 (talent_name + level로 unique 판단)
                existing = db.query(TalentLevel).filter(
                    TalentLevel.talent_name == level_data['talent_name'],
                    TalentLevel.level == level_data['level'],
                    TalentLevel.effect_name == level_data['effect_name']
                ).first()

                if existing:
                    # 업데이트
                    for key, value in level_data.items():
                        if hasattr(existing, key) and value:
                            setattr(existing, key, value)
                    logger.debug(f"Updated: {level_data['talent_name']} Level {level_data['level']}")
                else:
                    # 새로 생성
                    new_talent_level = TalentLevel(**level_data)
                    db.add(new_talent_level)
                    logger.debug(f"Added: {level_data['talent_name']} Level {level_data['level']}")

                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving talent level {level_data}: {e}")
                continue

        # 커밋
        db.commit()
        logger.info(f"Successfully saved {saved_count} talent level effects to database")

    def export_to_json(self, talent_levels_data: List[Dict], filename: str = "talent_levels.json"):
        """재능 레벨 데이터를 JSON 파일로 저장"""
        from pathlib import Path

        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(talent_levels_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Talent levels data exported to: {filepath}")


def main():
    """재능 레벨 크롤러 실행"""
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting talent levels crawler...")

    with TalentLevelsCrawler(delay=1.0) as crawler:
        # 모든 재능 레벨 크롤링
        talent_levels_data = crawler.crawl_all_talent_levels()

        if not talent_levels_data:
            logger.warning("No talent level data collected")
            return

        # JSON 저장
        crawler.export_to_json(talent_levels_data)

        # DB 저장
        with get_db_session() as db:
            crawler.save_talent_levels_to_db(talent_levels_data, db)

    logger.info("Talent levels crawler finished!")


if __name__ == "__main__":
    main()
