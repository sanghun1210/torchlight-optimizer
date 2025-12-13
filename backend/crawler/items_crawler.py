"""
아이템(Items) 데이터 크롤러
"""
import json
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from backend.crawler.base_crawler import BaseCrawler, DataParser
from backend.database.models import Item
from backend.database.db import get_db_session

logger = logging.getLogger(__name__)


class ItemsCrawler(BaseCrawler):
    """아이템 데이터 크롤링"""

    # 아이템 카테고리 URL
    ITEM_CATEGORIES = {
        'Weapon': {
            'One-Hand': 'https://tlidb.com/en/One-Hand_Weapon',
            'Two-Hand': 'https://tlidb.com/en/Two-Hand_Weapon',
            'Shield': 'https://tlidb.com/en/Shield',
        },
        'Armor': {
            'Helmet': 'https://tlidb.com/en/Helmet',
            'Body Armor': 'https://tlidb.com/en/Body_Armor',
            'Gloves': 'https://tlidb.com/en/Gloves',
            'Boots': 'https://tlidb.com/en/Boots',
        },
        'Accessory': {
            'Amulet': 'https://tlidb.com/en/Amulet',
            'Ring': 'https://tlidb.com/en/Ring',
            'Belt': 'https://tlidb.com/en/Belt',
        }
    }

    def crawl_all_items(self) -> List[Dict]:
        """
        모든 카테고리의 아이템 크롤링

        Returns:
            아이템 정보 딕셔너리 리스트
        """
        all_items = []

        for main_category, sub_categories in self.ITEM_CATEGORIES.items():
            for sub_category, url in sub_categories.items():
                logger.info(f"Crawling {main_category}/{sub_category} from: {url}")
                items = self.crawl_items_by_category(url, main_category, sub_category)
                all_items.extend(items)
                logger.info(f"Found {len(items)} {sub_category} items")

        logger.info(f"Total items found: {len(all_items)}")
        return all_items

    def crawl_items_by_category(
        self,
        url: str,
        main_category: str,
        sub_category: str
    ) -> List[Dict]:
        """
        특정 카테고리의 아이템 크롤링

        Args:
            url: 카테고리 페이지 URL
            main_category: 메인 카테고리 (Weapon, Armor, Accessory)
            sub_category: 서브 카테고리 (Helmet, Sword, etc.)

        Returns:
            아이템 정보 리스트
        """
        soup = self.fetch_page(url)
        if not soup:
            logger.error(f"Failed to fetch items page: {url}")
            return []

        items = []

        # 아이템 카드 찾기
        item_links = soup.find_all('a', href=True)

        for link in item_links:
            href = link.get('href', '')

            # 아이템 상세 페이지 링크 필터링
            if '/Item/' in href or f'/{sub_category.replace(" ", "_")}/' in href:
                img = link.find('img')
                if img:
                    item_data = self._parse_item_card(link, img, main_category, sub_category)
                    if item_data:
                        items.append(item_data)
                        logger.debug(f"Found item: {item_data.get('name', 'Unknown')}")

        # 중복 제거
        seen = set()
        unique_items = []
        for item in items:
            item_name = item.get('name', '')
            if item_name and item_name not in seen:
                seen.add(item_name)
                unique_items.append(item)

        return unique_items

    def _parse_item_card(
        self,
        link_element,
        img_element,
        main_category: str,
        sub_category: str
    ) -> Optional[Dict]:
        """
        아이템 카드에서 데이터 추출

        Args:
            link_element: 링크 엘리먼트
            img_element: 이미지 엘리먼트
            main_category: 메인 카테고리
            sub_category: 서브 카테고리

        Returns:
            아이템 데이터 딕셔너리
        """
        try:
            # 아이템 이름
            item_name = self.extract_text(link_element)

            if not item_name:
                href = link_element.get('href', '')
                item_name = href.split('/')[-1].replace('_', ' ').strip()

            # 이미지 URL
            image_url = DataParser.extract_image_url(img_element, self.BASE_URL)

            # 레어도 추론 (이미지나 클래스에서)
            rarity = self._infer_rarity(link_element, img_element)

            # 스탯 타입 추론 (이름이나 설명에서)
            stat_type = self._infer_stat_type(item_name)

            # 슬롯 결정
            slot = self._get_slot_from_category(sub_category)

            return {
                'name': item_name,
                'type': sub_category,
                'slot': slot,
                'rarity': rarity,
                'stat_type': stat_type,
                'image_url': image_url,
                'base_stats': '{}',  # 상세 페이지에서 추출 필요
                'special_effects': '[]',  # 상세 페이지에서 추출 필요
                'set_name': None,  # 상세 페이지에서 추출 필요
            }

        except Exception as e:
            logger.error(f"Error parsing item card: {e}")
            return None

    def _get_slot_from_category(self, sub_category: str) -> str:
        """카테고리에서 장비 슬롯 결정"""
        slot_mapping = {
            'Helmet': 'Head',
            'Body Armor': 'Chest',
            'Gloves': 'Hands',
            'Boots': 'Feet',
            'One-Hand': 'MainHand',
            'Two-Hand': 'TwoHand',
            'Shield': 'OffHand',
            'Amulet': 'Neck',
            'Ring': 'Finger',
            'Belt': 'Waist',
        }
        return slot_mapping.get(sub_category, sub_category)

    def _infer_rarity(self, link_element, img_element) -> str:
        """레어도 추론"""
        # 클래스나 스타일에서 레어도 정보 추출
        rarity_classes = ['common', 'rare', 'legendary', 'unique', 'epic']

        # 링크 엘리먼트의 클래스 확인
        classes = link_element.get('class', [])
        for rarity in rarity_classes:
            if any(rarity in c.lower() for c in classes):
                return rarity.capitalize()

        return 'Common'

    def _infer_stat_type(self, item_name: str) -> Optional[str]:
        """아이템 이름에서 스탯 타입 추론"""
        item_name_lower = item_name.lower()

        if 'str' in item_name_lower or 'strength' in item_name_lower:
            return 'STR'
        elif 'dex' in item_name_lower or 'dexterity' in item_name_lower:
            return 'DEX'
        elif 'int' in item_name_lower or 'intelligence' in item_name_lower:
            return 'INT'

        return None

    def save_items_to_db(self, items_data: List[Dict], db: Session):
        """
        크롤링한 아이템 데이터를 데이터베이스에 저장

        Args:
            items_data: 아이템 데이터 리스트
            db: 데이터베이스 세션
        """
        saved_count = 0

        for item_data in items_data:
            try:
                # 기존 아이템 확인
                existing_item = db.query(Item).filter(Item.name == item_data['name']).first()

                if existing_item:
                    # 업데이트
                    for key, value in item_data.items():
                        if hasattr(existing_item, key):
                            setattr(existing_item, key, value)
                    logger.info(f"Updated item: {item_data['name']}")
                else:
                    # 새로 생성
                    new_item = Item(**item_data)
                    db.add(new_item)
                    logger.info(f"Added new item: {item_data['name']}")

                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving item {item_data.get('name', 'Unknown')}: {e}")
                continue

        # 커밋
        db.commit()
        logger.info(f"Successfully saved {saved_count} items to database")

    def export_to_json(self, items_data: List[Dict], filename: str = "items.json"):
        """아이템 데이터를 JSON 파일로 저장"""
        from pathlib import Path

        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(items_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Items data exported to: {filepath}")


def main():
    """아이템 크롤러 실행 메인 함수"""
    logger.info("Starting items crawler...")

    with ItemsCrawler(delay=1.0) as crawler:
        # 1. 모든 카테고리의 아이템 크롤링
        items_data = crawler.crawl_all_items()

        if not items_data:
            logger.warning("No items data collected")
            return

        # 2. JSON으로 저장
        crawler.export_to_json(items_data)

        # 3. 데이터베이스에 저장
        with get_db_session() as db:
            crawler.save_items_to_db(items_data, db)

    logger.info("Items crawler finished!")


if __name__ == "__main__":
    main()
