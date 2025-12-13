"""
재능 노드(Talent Nodes) 데이터 크롤러
"""
import json
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from backend.crawler.base_crawler import BaseCrawler, DataParser
from backend.database.models import TalentNode
from backend.database.db import get_db_session

logger = logging.getLogger(__name__)


class TalentNodesCrawler(BaseCrawler):
    """재능 노드 데이터 크롤링"""

    TALENT_URL = "https://tlidb.com/en/Talent"

    def crawl_talent_nodes(self) -> List[Dict]:
        """
        재능 노드 페이지에서 모든 노드 정보 추출

        Returns:
            재능 노드 정보 딕셔너리 리스트
        """
        soup = self.fetch_page(self.TALENT_URL)
        if not soup:
            logger.error("Failed to fetch talent nodes page")
            return []

        talent_nodes = []

        # Border div 찾기 (아이템과 동일한 구조)
        borders = soup.find_all('div', class_=lambda x: x and 'border' in str(x).lower())
        logger.info(f"Found {len(borders)} border divs")

        # 재능 이미지를 포함한 border만 필터링
        skipped_count = 0
        borders_with_talent_img = 0

        for border in borders:
            img = border.find('img', src=lambda x: x and 'Talent' in x)
            if img:
                borders_with_talent_img += 1
                node_data = self._parse_talent_node(border, img)
                if node_data:
                    talent_nodes.append(node_data)
                    logger.debug(f"Found talent node: {node_data.get('name', 'Unknown')}")
                else:
                    skipped_count += 1

        logger.info(f"Borders with Talent images: {borders_with_talent_img}")
        logger.info(f"Skipped {skipped_count} items (professions or invalid data)")
        logger.info(f"Talent nodes before deduplication: {len(talent_nodes)}")

        # 중복 제거 (이름 기준)
        seen = set()
        unique_nodes = []
        for node in talent_nodes:
            node_name = node.get('name', '')
            if node_name and node_name not in seen:
                seen.add(node_name)
                unique_nodes.append(node)

        duplicates_removed = len(talent_nodes) - len(unique_nodes)
        logger.info(f"Removed {duplicates_removed} duplicates")
        logger.info(f"Total unique talent nodes found: {len(unique_nodes)}")

        # 코어와 일반 노드 통계
        core_count = sum(1 for n in unique_nodes if n.get('node_type') == 'Core')
        regular_count = sum(1 for n in unique_nodes if n.get('node_type') == 'Regular')
        logger.info(f"Core nodes: {core_count}, Regular nodes: {regular_count}")

        return unique_nodes

    def _parse_talent_node(self, border_element, img_element) -> Optional[Dict]:
        """
        재능 노드에서 데이터 추출

        Args:
            border_element: Border div 엘리먼트
            img_element: 이미지 엘리먼트

        Returns:
            재능 노드 데이터 딕셔너리
        """
        try:
            # 이미지 URL
            image_url = DataParser.extract_image_url(img_element, self.BASE_URL)

            # 노드 타입 판별 (Core vs Regular)
            is_core = 'CoreTalentIcon' in image_url
            node_type = 'Core' if is_core else 'Regular'

            # Border div에서 텍스트 추출
            text = border_element.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in text.split('\n') if line.strip()]

            if not lines:
                return None

            # Profession 정보 필터링 (직업은 Heroes 테이블에 이미 있음)
            # 직업은 다음 특징이 있음:
            # - "Main Stats:" 포함
            # - "Tags:" 포함하면서 실제 효과(+, %)가 아래에 없음
            text_combined = '\n'.join(lines)

            # "Main Stats:" 있으면 확실히 직업
            if 'Main Stats:' in text_combined:
                return None

            # "Tags:" 있고 그 뒤에 실제 스탯 효과가 없으면 직업
            if 'Tags:' in text_combined:
                # Tags 이후 텍스트 확인
                tags_idx = text_combined.find('Tags:')
                after_tags = text_combined[tags_idx:]
                # "Legacy", "Servant" 같은 키워드가 있으면 직업 설명
                if ('Legacy' in after_tags or 'Servant' in after_tags or
                    'Combat Expert' in after_tags or 'Fused with' in after_tags.lower()):
                    return None

            # 이름 추출
            name = lines[0]

            # Tier 추출 (이름에서)
            tier = None
            if 'Talent' in name:
                # "Micro Talent" -> tier="Micro"
                # "Legendary Medium Talent" -> tier="Legendary Medium"
                tier = name.replace(' Talent', '').strip()

            # God/클래스 및 효과 시작 위치 추출
            god_class = None
            effect_start_idx = 1

            if len(lines) > 1:
                # 코어 노드는 보통: Name, God Class, Effect...
                # 일반 노드는 보통: Name, God Class, Effect...
                god_class = lines[1]
                effect_start_idx = 2

            # 효과 추출 (나머지 라인들)
            effect_lines = lines[effect_start_idx:]
            effect = '\n'.join(effect_lines) if effect_lines else ''

            return {
                'name': name,
                'node_type': node_type,
                'god_class': god_class,
                'tier': tier,
                'effect': effect[:1000],  # 최대 1000자
                'image_url': image_url,
            }

        except Exception as e:
            logger.error(f"Error parsing talent node: {e}")
            return None

    def save_talent_nodes_to_db(self, nodes_data: List[Dict], db: Session):
        """
        크롤링한 재능 노드 데이터를 데이터베이스에 저장

        Args:
            nodes_data: 재능 노드 데이터 리스트
            db: 데이터베이스 세션
        """
        saved_count = 0

        for node_data in nodes_data:
            try:
                # 기존 노드 확인 (이름 기준)
                existing_node = db.query(TalentNode).filter(
                    TalentNode.name == node_data['name']
                ).first()

                if existing_node:
                    # 업데이트
                    for key, value in node_data.items():
                        if hasattr(existing_node, key):
                            setattr(existing_node, key, value)
                    logger.info(f"Updated talent node: {node_data['name']}")
                else:
                    # 새로 생성
                    new_node = TalentNode(**node_data)
                    db.add(new_node)
                    logger.info(f"Added new talent node: {node_data['name']}")

                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving talent node {node_data.get('name', 'Unknown')}: {e}")
                continue

        # 커밋
        db.commit()
        logger.info(f"Successfully saved {saved_count} talent nodes to database")

    def export_to_json(self, nodes_data: List[Dict], filename: str = "talent_nodes.json"):
        """재능 노드 데이터를 JSON 파일로 저장"""
        from pathlib import Path

        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(nodes_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Talent nodes data exported to: {filepath}")


def main():
    """재능 노드 크롤러 실행 메인 함수"""
    logger.info("Starting talent nodes crawler...")

    with TalentNodesCrawler(delay=0.5) as crawler:
        # 1. 재능 노드 크롤링
        nodes_data = crawler.crawl_talent_nodes()

        if not nodes_data:
            logger.warning("No talent nodes data collected")
            return

        # 2. JSON으로 저장
        crawler.export_to_json(nodes_data)

        # 3. 데이터베이스에 저장
        with get_db_session() as db:
            crawler.save_talent_nodes_to_db(nodes_data, db)

    logger.info("Talent nodes crawler finished!")


if __name__ == "__main__":
    main()
