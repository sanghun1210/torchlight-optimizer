"""
레전드 아이템(Legendary Gear) 데이터 크롤러
"""
import json
import logging
import re
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from backend.crawler.base_crawler import BaseCrawler, DataParser
from backend.database.models import Item
from backend.database.db import get_db_session

logger = logging.getLogger(__name__)


class LegendaryItemsCrawler(BaseCrawler):
    """레전드 아이템 데이터 크롤링"""

    LEGENDARY_GEAR_URL = "https://tlidb.com/en/Legendary_Gear"

    # 이미지 경로 패턴으로 아이템 타입 식별
    ITEM_TYPE_PATTERNS = {
        'Icon_Equip_Armor_': 'Body Armor',
        'Icon_Equip_Helmet_': 'Helmet',
        'Icon_Equip_Shoes_': 'Boots',
        'Icon_Equip_Gloves_': 'Gloves',
        'Icon_Equip_Weapon_': 'Weapon',
        'Icon_Equip_Amulet_': 'Amulet',
        'Icon_Equip_Ring_': 'Ring',
        'Icon_Equip_Belt_': 'Belt',
        'Icon_Equip_Shield_': 'Shield',
        'Icon_Equip_TalentSlate_': 'Talent Slate',
    }

    def crawl_legendary_items(self) -> List[Dict]:
        """
        레전드 아이템 페이지에서 모든 아이템 정보 추출

        Returns:
            아이템 정보 딕셔너리 리스트
        """
        soup = self.fetch_page(self.LEGENDARY_GEAR_URL)
        if not soup:
            logger.error("Failed to fetch legendary gear page")
            return []

        items = []

        # 아이템 이미지 찾기 (Icon_Equip_ 패턴)
        item_images = soup.find_all('img', src=lambda x: x and 'Icon_Equip_' in x)
        logger.info(f"Found {len(item_images)} legendary item images")

        for img in item_images:
            # 이미지를 포함한 링크 찾기
            link = img.find_parent('a')
            if link:
                item_data = self._parse_item_card(link, img, soup)
                if item_data:
                    items.append(item_data)
                    logger.debug(f"Found item: {item_data.get('name', 'Unknown')}")

        # 중복 제거 (이름 기준)
        seen = set()
        unique_items = []
        for item in items:
            item_name = item.get('name', '')
            if item_name and item_name not in seen:
                seen.add(item_name)
                unique_items.append(item)

        logger.info(f"Total unique legendary items found: {len(unique_items)}")
        return unique_items

    def _parse_item_card(self, link_element, img_element, soup) -> Optional[Dict]:
        """
        아이템 카드에서 데이터 추출

        Args:
            link_element: 링크 엘리먼트
            img_element: 이미지 엘리먼트
            soup: BeautifulSoup 객체

        Returns:
            아이템 데이터 딕셔너리
        """
        try:
            # 아이템 이름 (링크 href 또는 텍스트)
            href = link_element.get('href', '')
            item_name = href.strip('/')

            # 이미지 URL
            image_url = DataParser.extract_image_url(img_element, self.BASE_URL)

            # 이미지 경로에서 아이템 타입 식별
            item_type = self._identify_item_type(image_url)
            slot = self._get_slot_from_type(item_type)

            # 링크 다음 텍스트 링크에서 아이템 이름 확인
            next_link = link_element.find_next_sibling('a')
            if next_link:
                display_name = self.extract_text(next_link)
                if display_name and not display_name.startswith('http'):
                    item_name = display_name

            # 아이템 이름 정리 (언더스코어를 공백으로)
            item_name_clean = item_name.replace('_', ' ').strip()

            # 요구 레벨 찾기
            required_level = None
            next_text = link_element.find_next_sibling(string=True)
            if next_text:
                level_match = re.search(r'Require lv (\d+)', next_text)
                if level_match:
                    required_level = int(level_match.group(1))

            # 아이템 효과/설명 찾기
            description = ""
            special_effects = []

            # 링크 이후의 텍스트들을 수집
            current = link_element.find_next_sibling()
            effect_lines = []

            while current:
                if current.name == 'a' and 'Icon_Equip_' in str(current):
                    # 다음 아이템 시작
                    break

                text = self.extract_text(current) if current.name else str(current)
                text = text.strip()

                if text and text != '* * *' and not text.startswith('Require lv'):
                    if len(text) > 5:  # 의미있는 텍스트만
                        effect_lines.append(text)

                current = current.find_next_sibling()

                # 최대 10개 라인까지만
                if len(effect_lines) >= 10:
                    break

            # 효과 리스트로 저장
            special_effects = effect_lines[:5]  # 최대 5개 효과
            if effect_lines:
                description = ' '.join(effect_lines[:2])  # 첫 2줄을 설명으로

            return {
                'name': item_name_clean,
                'type': item_type,
                'slot': slot,
                'rarity': 'Legendary',
                'stat_type': None,  # 레전드 아이템은 범용
                'base_stats': json.dumps({}),
                'special_effects': json.dumps(special_effects),
                'set_name': None,
                'image_url': image_url,
                'required_level': required_level,
            }

        except Exception as e:
            logger.error(f"Error parsing legendary item card: {e}")
            return None

    def _identify_item_type(self, image_url: str) -> str:
        """이미지 URL에서 아이템 타입 식별"""
        if not image_url:
            return 'Unknown'

        for pattern, item_type in self.ITEM_TYPE_PATTERNS.items():
            if pattern in image_url:
                return item_type

        return 'Unknown'

    def _get_slot_from_type(self, item_type: str) -> str:
        """아이템 타입에서 장비 슬롯 결정"""
        slot_mapping = {
            'Helmet': 'Head',
            'Body Armor': 'Chest',
            'Gloves': 'Hands',
            'Boots': 'Feet',
            'Weapon': 'MainHand',
            'Shield': 'OffHand',
            'Amulet': 'Neck',
            'Ring': 'Finger',
            'Belt': 'Waist',
            'Talent Slate': 'Special',
        }
        return slot_mapping.get(item_type, item_type)

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
                        if hasattr(existing_item, key) and key != 'required_level':
                            setattr(existing_item, key, value)
                    logger.info(f"Updated item: {item_data['name']}")
                else:
                    # required_level 제거 (데이터베이스 모델에 없음)
                    save_data = {k: v for k, v in item_data.items() if k != 'required_level'}

                    # 새로 생성
                    new_item = Item(**save_data)
                    db.add(new_item)
                    logger.info(f"Added new item: {item_data['name']}")

                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving item {item_data.get('name', 'Unknown')}: {e}")
                continue

        # 커밋
        db.commit()
        logger.info(f"Successfully saved {saved_count} legendary items to database")

    def export_to_json(self, items_data: List[Dict], filename: str = "legendary_items.json"):
        """아이템 데이터를 JSON 파일로 저장"""
        from pathlib import Path

        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(items_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Legendary items data exported to: {filepath}")


def main():
    """레전드 아이템 크롤러 실행 메인 함수"""
    logger.info("Starting legendary items crawler...")

    with LegendaryItemsCrawler(delay=1.0) as crawler:
        # 1. 레전드 아이템 크롤링
        items_data = crawler.crawl_legendary_items()

        if not items_data:
            logger.warning("No legendary items data collected")
            return

        # 2. JSON으로 저장
        crawler.export_to_json(items_data)

        # 3. 데이터베이스에 저장
        with get_db_session() as db:
            crawler.save_items_to_db(items_data, db)

    logger.info("Legendary items crawler finished!")


if __name__ == "__main__":
    main()
