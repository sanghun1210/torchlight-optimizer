"""
운명(Destiny/Fate) 데이터 크롤러
"""
import json
import logging
import re
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from backend.crawler.base_crawler import BaseCrawler, DataParser
from backend.database.models import Destiny
from backend.database.db import get_db_session

logger = logging.getLogger(__name__)


class DestinyCrawler(BaseCrawler):
    """운명 데이터 크롤링"""

    DESTINY_URL = "https://tlidb.com/en/Destiny"

    def crawl_destinies(self) -> List[Dict]:
        """
        운명 페이지에서 모든 운명 정보 추출

        Returns:
            운명 정보 딕셔너리 리스트
        """
        soup = self.fetch_page(self.DESTINY_URL)
        if not soup:
            logger.error("Failed to fetch destiny page")
            return []

        destinies = []

        # Border div 찾기 (아이템/재능과 동일한 구조)
        borders = soup.find_all('div', class_=lambda x: x and 'border' in str(x).lower())
        logger.info(f"Found {len(borders)} border divs")

        # Destiny/Fate 이미지를 포함한 border만 필터링
        for border in borders:
            img = border.find('img', src=lambda x: x and 'DestinyFate' in x or (x and 'Fate' in x))
            if img:
                destiny_data = self._parse_destiny(border, img)
                if destiny_data:
                    destinies.append(destiny_data)
                    logger.debug(f"Found destiny: {destiny_data.get('name', 'Unknown')}")

        # 중복 제거 (이름 기준)
        seen = set()
        unique_destinies = []
        for destiny in destinies:
            name = destiny.get('name', '')
            if name and name not in seen:
                seen.add(name)
                unique_destinies.append(destiny)

        logger.info(f"Total unique destinies found: {len(unique_destinies)}")
        return unique_destinies

    def _parse_destiny(self, border_element, img_element) -> Optional[Dict]:
        """
        운명에서 데이터 추출

        Args:
            border_element: Border div 엘리먼트
            img_element: 이미지 엘리먼트

        Returns:
            운명 데이터 딕셔너리
        """
        try:
            # 이미지 URL
            image_url = DataParser.extract_image_url(img_element, self.BASE_URL)

            # Border div에서 텍스트 추출
            text = border_element.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in text.split('\n') if line.strip()]

            if not lines:
                return None

            # 첫 번째 줄: 전체 이름 (예: "Micro Fate: Fire Resistance")
            full_name = lines[0]

            # Tier와 Category 분리
            # "Micro Fate: Fire Resistance" -> tier="Micro", category="Fire Resistance"
            tier = None
            category = None

            if 'Fate:' in full_name:
                parts = full_name.split('Fate:')
                if len(parts) == 2:
                    tier = parts[0].strip()  # "Micro"
                    category = parts[1].strip()  # "Fire Resistance"

            # 효과 추출 (나머지 라인들)
            effect_lines = lines[1:]
            effect = '\n'.join(effect_lines) if effect_lines else ''

            # 스탯 범위 추출 (예: "(5–7)", "(14–18)")
            stat_range = None
            range_match = re.search(r'\((\d+)–(\d+)\)', effect)
            if range_match:
                stat_range = f"({range_match.group(1)}-{range_match.group(2)})"

            return {
                'name': full_name,
                'tier': tier,
                'category': category,
                'effect': effect[:500],  # 최대 500자
                'stat_range': stat_range,
                'image_url': image_url,
            }

        except Exception as e:
            logger.error(f"Error parsing destiny: {e}")
            return None

    def save_destinies_to_db(self, destinies_data: List[Dict], db: Session):
        """
        크롤링한 운명 데이터를 데이터베이스에 저장

        Args:
            destinies_data: 운명 데이터 리스트
            db: 데이터베이스 세션
        """
        saved_count = 0

        for destiny_data in destinies_data:
            try:
                # 기존 운명 확인 (이름 기준)
                existing_destiny = db.query(Destiny).filter(
                    Destiny.name == destiny_data['name']
                ).first()

                if existing_destiny:
                    # 업데이트
                    for key, value in destiny_data.items():
                        if hasattr(existing_destiny, key):
                            setattr(existing_destiny, key, value)
                    logger.info(f"Updated destiny: {destiny_data['name']}")
                else:
                    # 새로 생성
                    new_destiny = Destiny(**destiny_data)
                    db.add(new_destiny)
                    logger.info(f"Added new destiny: {destiny_data['name']}")

                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving destiny {destiny_data.get('name', 'Unknown')}: {e}")
                continue

        # 커밋
        db.commit()
        logger.info(f"Successfully saved {saved_count} destinies to database")

    def export_to_json(self, destinies_data: List[Dict], filename: str = "destinies.json"):
        """운명 데이터를 JSON 파일로 저장"""
        from pathlib import Path

        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(destinies_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Destinies data exported to: {filepath}")


def main():
    """운명 크롤러 실행 메인 함수"""
    logger.info("Starting destiny crawler...")

    with DestinyCrawler(delay=0.5) as crawler:
        # 1. 운명 크롤링
        destinies_data = crawler.crawl_destinies()

        if not destinies_data:
            logger.warning("No destinies data collected")
            return

        # 2. JSON으로 저장
        crawler.export_to_json(destinies_data)

        # 3. 데이터베이스에 저장
        with get_db_session() as db:
            crawler.save_destinies_to_db(destinies_data, db)

    logger.info("Destiny crawler finished!")


if __name__ == "__main__":
    main()
