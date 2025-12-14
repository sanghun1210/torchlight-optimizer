"""
레전드 아이템(Legendary Gear) 데이터 크롤러 v2 - 개선된 파싱
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


class LegendaryItemsCrawlerV2(BaseCrawler):
    """레전드 아이템 데이터 크롤링 v2"""

    LEGENDARY_GEAR_URL = "https://tlidb.com/ko/Legendary_Gear"

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
                item_data = self._parse_item_card(link, img)
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

    def _parse_item_card(self, link_element, img_element) -> Optional[Dict]:
        """
        아이템 카드에서 데이터 추출

        Args:
            link_element: 링크 엘리먼트 (이미지 포함)
            img_element: 이미지 엘리먼트

        Returns:
            아이템 데이터 딕셔너리
        """
        try:
            # 이미지 URL
            image_url = DataParser.extract_image_url(img_element, self.BASE_URL)

            # 이미지 경로에서 아이템 타입 식별
            item_type = self._identify_item_type(image_url)
            slot = self._get_slot_from_type(item_type)

            # link의 부모 -> 조부모 -> 정보 div 찾기
            parent = link_element.parent  # div.flex-shrink-0
            if not parent:
                return None

            grandparent = parent.parent  # div.d-flex.border-top.rounded
            if not grandparent:
                return None

            # 조부모의 자식 중 flex-grow-1 클래스 찾기 (아이템 정보 포함)
            info_div = grandparent.find('div', class_='flex-grow-1')
            if not info_div:
                logger.warning(f"No info div found for item")
                return None

            # 정보 div에서 텍스트 추출
            info_text = info_div.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in info_text.split('\n') if line.strip()]

            if not lines:
                return None

            # 첫 번째 줄: 아이템 이름
            item_name = lines[0]

            # 요구 레벨 찾기
            required_level = None
            special_effects = []

            for line in lines[1:]:
                # "Require lv X" 또는 "요구 레벨 X" 또는 "Lv X" 패턴
                if any(keyword in line.lower() for keyword in ['require lv', '요구 레벨', 'lv', '레벨']):
                    level_match = re.search(r'(\d+)', line)
                    if level_match and not required_level:  # 첫 번째 숫자만
                        required_level = int(level_match.group(1))
                # 특수 효과 (모든 옵션 텍스트 수집)
                elif any(char in line for char in ['+', '-', '%', '증가', '감소', '추가']) or len(line) > 5:
                    # 너무 짧은 라인 제외
                    if len(line) > 3:
                        special_effects.append(line)

            # 설명: 모든 효과를 합침
            description = ' | '.join(special_effects[:5]) if special_effects else ''

            return {
                'name': item_name,
                'type': item_type,
                'slot': slot,
                'rarity': 'Legendary',
                'stat_type': None,  # 레전드 아이템은 범용
                'base_stats': json.dumps({}),
                'special_effects': json.dumps(special_effects),  # 모든 효과 포함
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
                # required_level 제거 (데이터베이스 모델에 없음)
                save_data = {k: v for k, v in item_data.items() if k != 'required_level'}

                # 기존 아이템 확인
                existing_item = db.query(Item).filter(Item.name == save_data['name']).first()

                if existing_item:
                    # 업데이트
                    for key, value in save_data.items():
                        if hasattr(existing_item, key):
                            setattr(existing_item, key, value)
                    logger.info(f"Updated item: {save_data['name']}")
                else:
                    # 새로 생성
                    new_item = Item(**save_data)
                    db.add(new_item)
                    logger.info(f"Added new item: {save_data['name']}")

                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving item {item_data.get('name', 'Unknown')}: {e}")
                continue

        # 커밋
        db.commit()
        logger.info(f"Successfully saved {saved_count} legendary items to database")

    def export_to_json(self, items_data: List[Dict], filename: str = "legendary_items_v2.json"):
        """아이템 데이터를 JSON 파일로 저장"""
        from pathlib import Path

        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(items_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Legendary items data exported to: {filepath}")


def main():
    """레전드 아이템 크롤러 v2 실행 메인 함수"""
    logger.info("Starting legendary items crawler v2...")

    with LegendaryItemsCrawlerV2(delay=0.5) as crawler:
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

    logger.info("Legendary items crawler v2 finished!")


if __name__ == "__main__":
    main()
