"""
영웅(Heroes) 데이터 크롤러
"""
import json
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from backend.crawler.base_crawler import BaseCrawler, DataParser
from backend.database.models import Hero
from backend.database.db import get_db_session

logger = logging.getLogger(__name__)


class HeroesCrawler(BaseCrawler):
    """영웅 데이터 크롤링"""

    HEROES_URL = "https://tlidb.com/en/Hero"

    def crawl_heroes_list(self) -> List[Dict]:
        """
        영웅 목록 페이지에서 모든 영웅 정보 추출

        Returns:
            영웅 정보 딕셔너리 리스트
        """
        soup = self.fetch_page(self.HEROES_URL)
        if not soup:
            logger.error("Failed to fetch heroes list page")
            return []

        heroes = []

        # 영웅 이미지 찾기 (Portrait 패턴)
        hero_images = soup.find_all('img', src=lambda x: x and 'Portrait' in x)
        logger.info(f"Found {len(hero_images)} hero images")

        for img in hero_images:
            # 이미지를 포함한 링크 찾기
            link = img.find_parent('a')
            if link:
                hero_data = self._parse_hero_card(link, img)
                if hero_data:
                    heroes.append(hero_data)
                    logger.info(f"Found hero: {hero_data.get('name', 'Unknown')} ({hero_data.get('talent', '')})")

        # 중복 제거 (talent 기준)
        seen = set()
        unique_heroes = []
        for hero in heroes:
            talent = hero.get('talent', '')
            if talent and talent not in seen:
                seen.add(talent)
                unique_heroes.append(hero)

        logger.info(f"Total unique heroes found: {len(unique_heroes)}")
        return unique_heroes

    def _parse_hero_card(self, link_element, img_element) -> Optional[Dict]:
        """
        영웅 카드에서 데이터 추출

        Args:
            link_element: 링크 엘리먼트
            img_element: 이미지 엘리먼트

        Returns:
            영웅 데이터 딕셔너리
        """
        try:
            # 이미지 URL에서 영웅 이름 추출
            # 예: UI_Portrait_Rehan_icon_128.webp -> Rehan
            image_url = DataParser.extract_image_url(img_element, self.BASE_URL)
            hero_name_from_url = ""
            if image_url and 'Portrait/' in image_url:
                parts = image_url.split('Portrait/')[-1].split('/')
                if len(parts) > 0:
                    hero_name_from_url = parts[0]

            # 링크에서 talent 이름 추출
            href = link_element.get('href', '')
            talent = href.strip('/')  # 앞뒤 슬래시 제거

            # 링크 텍스트에서 영웅 이름과 talent 추출
            link_text = self.extract_text(link_element)

            # 텍스트 파싱: "Berserker Rehan|Anger" 또는 "Rehan|Anger" 형식
            hero_name = hero_name_from_url  # 기본값
            talent_display = talent

            if '|' in link_text:
                parts = link_text.split('|')
                hero_full_name = parts[0].strip()
                talent_display = parts[1].strip()

                # "Berserker Rehan"에서 "Rehan" 추출 (마지막 단어)
                if ' ' in hero_full_name:
                    hero_name = hero_full_name.split()[-1]
                else:
                    hero_name = hero_full_name
            elif link_text and not link_text.startswith('http'):
                hero_name = link_text

            # 링크의 부모나 형제 요소에서 설명 찾기
            description = ""

            # 방법 1: 다음 형제 요소 확인
            next_elem = link_element.find_next_sibling()
            while next_elem and description == "":
                if next_elem.name in ['p', 'div']:
                    desc_text = self.extract_text(next_elem)
                    if desc_text and len(desc_text) > 10:  # 의미있는 텍스트만
                        description = desc_text
                        break
                next_elem = next_elem.find_next_sibling()

            # God type 추론
            god_type = self._infer_god_type(image_url, talent)

            return {
                'name': hero_name,
                'god_type': god_type,
                'talent': talent,
                'talent_display': talent_display,
                'description': description,
                'image_url': image_url,
                'talent_url': self.get_absolute_url(href) if href else ''
            }

        except Exception as e:
            logger.error(f"Error parsing hero card: {e}")
            return None

    def _infer_god_type(self, image_url: str, talent: str) -> str:
        """
        이미지 URL이나 talent 이름에서 God type 추론

        신 계열 매핑은 나중에 수동으로 보완 가능
        """
        # 기본값
        return "Unknown"

    def save_heroes_to_db(self, heroes_data: List[Dict], db: Session):
        """
        크롤링한 영웅 데이터를 데이터베이스에 저장

        Args:
            heroes_data: 영웅 데이터 리스트
            db: 데이터베이스 세션
        """
        saved_count = 0

        for hero_data in heroes_data:
            try:
                # 기존 영웅 확인 (name 기준)
                existing_hero = db.query(Hero).filter(Hero.name == hero_data['name']).first()

                if existing_hero:
                    # 업데이트
                    existing_hero.god_type = hero_data.get('god_type', existing_hero.god_type)
                    existing_hero.talent = hero_data.get('talent', existing_hero.talent)
                    existing_hero.description = hero_data.get('description', existing_hero.description)
                    existing_hero.image_url = hero_data.get('image_url', existing_hero.image_url)
                    logger.info(f"Updated hero: {hero_data['name']}")
                else:
                    # 새로 생성
                    new_hero = Hero(
                        name=hero_data['name'],
                        god_type=hero_data.get('god_type', 'Unknown'),
                        talent=hero_data.get('talent', ''),
                        description=hero_data.get('description', ''),
                        image_url=hero_data.get('image_url', ''),
                        popularity_score=0.0
                    )
                    db.add(new_hero)
                    logger.info(f"Added new hero: {hero_data['name']}")

                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving hero {hero_data.get('name', 'Unknown')}: {e}")
                continue

        # 커밋
        db.commit()
        logger.info(f"Successfully saved {saved_count} heroes to database")

    def export_to_json(self, heroes_data: List[Dict], filename: str = "heroes.json"):
        """영웅 데이터를 JSON 파일로 저장"""
        import os
        from pathlib import Path

        # data 디렉토리에 저장
        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(heroes_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Heroes data exported to: {filepath}")


def main():
    """영웅 크롤러 실행 메인 함수"""
    logger.info("Starting heroes crawler...")

    with HeroesCrawler(delay=1.0) as crawler:
        # 1. 영웅 목록 크롤링
        heroes_data = crawler.crawl_heroes_list()

        if not heroes_data:
            logger.warning("No heroes data collected")
            return

        # 2. JSON으로 저장
        crawler.export_to_json(heroes_data)

        # 3. 데이터베이스에 저장
        with get_db_session() as db:
            crawler.save_heroes_to_db(heroes_data, db)

    logger.info("Heroes crawler finished!")


if __name__ == "__main__":
    main()
