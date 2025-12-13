"""
영웅(Heroes) 데이터 크롤러 v2 - 개별 페이지 크롤링
"""
import json
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from backend.crawler.base_crawler import BaseCrawler, DataParser
from backend.database.models import Hero
from backend.database.db import get_db_session

logger = logging.getLogger(__name__)


class HeroesCrawlerV2(BaseCrawler):
    """영웅 데이터 크롤링 - 개별 페이지 방문"""

    HEROES_URL = "https://tlidb.com/en/Hero"

    def crawl_all_heroes(self, detailed: bool = True) -> List[Dict]:
        """
        모든 영웅/재능 크롤링

        Args:
            detailed: True면 개별 페이지 방문, False면 목록만

        Returns:
            영웅 정보 딕셔너리 리스트
        """
        logger.info(f"Crawling heroes from: {self.HEROES_URL}")

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
                href = link.get('href', '')
                talent_url = self.get_absolute_url(href)

                # 링크 텍스트에서 기본 정보 추출
                link_text = self.extract_text(link)

                # 기본 정보
                hero_data = {
                    'talent_url': talent_url,
                    'image_url': DataParser.extract_image_url(img, self.BASE_URL),
                    'link_text': link_text,
                }

                # 상세 정보 크롤링
                if detailed and talent_url:
                    details = self._fetch_hero_details(talent_url, link_text)
                    hero_data.update(details)

                heroes.append(hero_data)
                logger.debug(f"Crawled hero: {hero_data.get('talent', 'Unknown')}")

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

    def _fetch_hero_details(self, hero_url: str, link_text: str) -> Dict:
        """
        개별 영웅/재능 페이지에서 상세 정보 추출

        Args:
            hero_url: 영웅 상세 페이지 URL
            link_text: 링크 텍스트 (예: "Berserker Rehan|Seething Silhouette")

        Returns:
            상세 정보 딕셔너리
        """
        details = {
            'name': '',
            'god_type': 'Unknown',
            'talent': '',
            'description': '',
        }

        soup = self.fetch_page(hero_url)
        if not soup:
            logger.warning(f"Failed to fetch hero details: {hero_url}")
            return details

        try:
            # URL에서 talent 이름 추출
            # 예: https://tlidb.com/en/Seething_Silhouette -> Seething_Silhouette
            talent_from_url = hero_url.rstrip('/').split('/')[-1]
            details['talent'] = talent_from_url.replace('_', ' ')

            # 링크 텍스트 파싱: "Berserker Rehan|Seething Silhouette" 또는 "Rehan|Anger"
            if '|' in link_text:
                parts = link_text.split('|')
                hero_part = parts[0].strip()  # "Berserker Rehan" 또는 "Rehan"
                talent_part = parts[1].strip() if len(parts) > 1 else ''

                if talent_part:
                    details['talent'] = talent_part

                # God type과 영웅 이름 분리
                # "Berserker Rehan" -> god_type="Berserker", name="Rehan"
                # "Rehan" -> name="Rehan"
                words = hero_part.split()
                if len(words) >= 2:
                    details['god_type'] = words[0]  # 첫 단어는 클래스/God
                    details['name'] = ' '.join(words[1:])  # 나머지는 영웅 이름
                elif len(words) == 1:
                    details['name'] = words[0]

            # 페이지에서 "Class|HeroName" 패턴 찾기
            # 예: "Berserker|Rehan"
            class_hero_elements = soup.find_all(string=lambda x: x and '|' in str(x) and len(str(x).strip()) < 50)
            for elem in class_hero_elements:
                text = elem.strip()
                if '|' in text and not text.startswith('http'):
                    parts = text.split('|')
                    if len(parts) == 2:
                        potential_class = parts[0].strip()
                        potential_name = parts[1].strip()

                        # 유효한 클래스/영웅 이름인지 확인 (단어가 너무 길지 않음)
                        if len(potential_class.split()) <= 2 and len(potential_name.split()) <= 2:
                            if details['god_type'] == 'Unknown':
                                details['god_type'] = potential_class
                            if not details['name']:
                                details['name'] = potential_name
                            break

            # 설명 추출
            # card-body 클래스에서 영웅 설명 찾기
            card_bodies = soup.find_all('div', class_='card-body')
            for card_body in card_bodies:
                text = card_body.get_text(strip=True)
                # 충분히 긴 텍스트이고, 영웅 이름이나 재능 이름을 포함하면 설명으로 판단
                if len(text) > 50 and (details['name'] in text or details['talent'] in text):
                    # "God|Name" 접두사 제거
                    cleaned_text = self._clean_description(text, details['god_type'], details['name'])
                    details['description'] = cleaned_text[:500]  # 최대 500자
                    break

            # 설명을 못 찾았다면 첫 번째 card-body 사용
            if not details['description'] and card_bodies:
                text = card_bodies[0].get_text(strip=True)
                if len(text) > 50:
                    # "Blessed by" 같은 패턴으로 시작하는 텍스트 찾기
                    if any(keyword in text for keyword in ['Blessed', 'gains', 'has a chance', 'summon']):
                        cleaned_text = self._clean_description(text, details['god_type'], details['name'])
                        details['description'] = cleaned_text[:500]

        except Exception as e:
            logger.error(f"Error parsing hero details from {hero_url}: {e}")

        return details

    def _clean_description(self, text: str, god_type: str, name: str) -> str:
        """
        설명에서 "God|Name" 접두사 제거

        Args:
            text: 원본 텍스트
            god_type: God/클래스 타입
            name: 영웅 이름

        Returns:
            정리된 텍스트
        """
        # "Berserker|Rehan" 같은 패턴 제거
        if god_type and name:
            prefix = f"{god_type}|{name}"
            if text.startswith(prefix):
                text = text[len(prefix):].strip()

        return text

    def save_heroes_to_db(self, heroes_data: List[Dict], db: Session):
        """
        크롤링한 영웅 데이터를 데이터베이스에 저장
        """
        saved_count = 0

        for hero_data in heroes_data:
            try:
                # 필요한 필드만 추출
                save_data = {
                    'name': hero_data.get('name', ''),
                    'god_type': hero_data.get('god_type', 'Unknown'),
                    'talent': hero_data.get('talent', ''),
                    'description': hero_data.get('description', ''),
                    'image_url': hero_data.get('image_url', ''),
                }

                # talent이 비어있으면 스킵
                if not save_data['talent']:
                    logger.warning(f"Skipping hero with empty talent: {save_data}")
                    continue

                # 기존 영웅 확인 (talent 기준 - talent이 unique)
                existing_hero = db.query(Hero).filter(Hero.talent == save_data['talent']).first()

                if existing_hero:
                    # 업데이트
                    for key, value in save_data.items():
                        if hasattr(existing_hero, key) and value:  # 값이 있을 때만 업데이트
                            setattr(existing_hero, key, value)
                    logger.info(f"Updated hero: {save_data['name']} ({save_data['talent']})")
                else:
                    # 새로 생성
                    new_hero = Hero(**save_data)
                    db.add(new_hero)
                    logger.info(f"Added new hero: {save_data['name']} ({save_data['talent']})")

                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving hero {hero_data.get('name', 'Unknown')}: {e}")
                continue

        # 커밋
        db.commit()
        logger.info(f"Successfully saved {saved_count} heroes to database")

    def export_to_json(self, heroes_data: List[Dict], filename: str = "heroes_v2.json"):
        """영웅 데이터를 JSON 파일로 저장"""
        from pathlib import Path

        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(heroes_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Heroes data exported to: {filepath}")


def main():
    """영웅 크롤러 v2 실행 메인 함수"""
    logger.info("Starting heroes crawler v2 (with detail pages)...")

    with HeroesCrawlerV2(delay=0.5) as crawler:
        # 1. 모든 영웅 크롤링 (상세 정보 포함)
        heroes_data = crawler.crawl_all_heroes(detailed=True)

        if not heroes_data:
            logger.warning("No heroes data collected")
            return

        # 2. JSON으로 저장
        crawler.export_to_json(heroes_data)

        # 3. 데이터베이스에 저장
        with get_db_session() as db:
            crawler.save_heroes_to_db(heroes_data, db)

    logger.info("Heroes crawler v2 finished!")


if __name__ == "__main__":
    main()
