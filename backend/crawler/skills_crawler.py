"""
스킬(Skills) 데이터 크롤러
"""
import json
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from backend.crawler.base_crawler import BaseCrawler, DataParser
from backend.database.models import Skill
from backend.database.db import get_db_session

logger = logging.getLogger(__name__)


class SkillsCrawler(BaseCrawler):
    """스킬 데이터 크롤링"""

    # 스킬 카테고리 URL
    SKILL_CATEGORIES = {
        'Active': 'https://tlidb.com/en/Active_Skill',
        'Support': 'https://tlidb.com/en/Support_Skill',
        'Passive': 'https://tlidb.com/en/Passive_Skill',
        'Activation Medium': 'https://tlidb.com/en/Activation_Medium_Skill',
        'Noble Support': 'https://tlidb.com/en/Noble_Support_Skill',
        'Magnificent Support': 'https://tlidb.com/en/Magnificent_Support_Skill',
    }

    def crawl_all_skills(self) -> List[Dict]:
        """
        모든 카테고리의 스킬 크롤링

        Returns:
            스킬 정보 딕셔너리 리스트
        """
        all_skills = []

        for category, url in self.SKILL_CATEGORIES.items():
            logger.info(f"Crawling {category} skills from: {url}")
            skills = self.crawl_skills_by_category(url, category)
            all_skills.extend(skills)
            logger.info(f"Found {len(skills)} {category} skills")

        logger.info(f"Total skills found: {len(all_skills)}")
        return all_skills

    def crawl_skills_by_category(self, url: str, category: str) -> List[Dict]:
        """
        특정 카테고리의 스킬 크롤링

        Args:
            url: 카테고리 페이지 URL
            category: 스킬 카테고리

        Returns:
            스킬 정보 리스트
        """
        soup = self.fetch_page(url)
        if not soup:
            logger.error(f"Failed to fetch skills page: {url}")
            return []

        skills = []

        # 스킬 이미지 찾기 (Icon_Skill_ 패턴)
        skill_images = soup.find_all('img', src=lambda x: x and 'Icon_Skill_' in x)
        logger.info(f"Found {len(skill_images)} skill images in {category}")

        for img in skill_images:
            # 이미지를 포함한 링크 찾기
            link = img.find_parent('a')
            if link:
                skill_data = self._parse_skill_card(link, img, category)
                if skill_data:
                    skills.append(skill_data)
                    logger.debug(f"Found skill: {skill_data.get('name', 'Unknown')}")

        # 중복 제거
        seen = set()
        unique_skills = []
        for skill in skills:
            skill_name = skill.get('name', '')
            if skill_name and skill_name not in seen:
                seen.add(skill_name)
                unique_skills.append(skill)

        return unique_skills

    def _parse_skill_card(self, link_element, img_element, category: str) -> Optional[Dict]:
        """
        스킬 카드에서 데이터 추출

        Args:
            link_element: 링크 엘리먼트
            img_element: 이미지 엘리먼트
            category: 스킬 카테고리

        Returns:
            스킬 데이터 딕셔너리
        """
        try:
            # 스킬 이름 (링크 텍스트 또는 이미지 URL에서 추출)
            skill_name = self.extract_text(link_element)

            # 이미지 URL
            image_url = DataParser.extract_image_url(img_element, self.BASE_URL)

            # 이름이 없으면 이미지 URL에서 추출
            # 예: Icon_Skill_Leapslam_128.webp -> Leapslam
            if not skill_name or skill_name.startswith('http'):
                if image_url and 'Icon_Skill_' in image_url:
                    filename = image_url.split('/')[-1]
                    # Icon_Skill_Leapslam_128.webp -> Leapslam
                    parts = filename.replace('Icon_Skill_', '').replace('_128', '').replace('.webp', '')
                    skill_name = parts.replace('_', ' ').strip()

            # 링크의 다음 형제 요소에서 태그와 설명 찾기
            tags = []
            description = ""

            # 방법 1: 링크의 부모 요소에서 찾기
            parent = link_element.find_parent()
            if parent:
                # 다음 형제 요소들을 순회
                next_elem = link_element.find_next_sibling()
                tag_found = False

                while next_elem:
                    elem_text = self.extract_text(next_elem)

                    # 태그 라인: 쉼표로 구분된 텍스트 (첫 번째 발견)
                    if not tag_found and ',' in elem_text and len(elem_text) < 200:
                        tags = DataParser.parse_tags(elem_text)
                        tag_found = True
                    # 설명: 긴 텍스트
                    elif len(elem_text) > 20 and not description:
                        description = elem_text
                        break

                    next_elem = next_elem.find_next_sibling()

            # 데미지 타입 추론 (태그에서)
            damage_type = self._infer_damage_type(tags)

            return {
                'name': skill_name,
                'type': category,
                'description': description,
                'tags': json.dumps(tags),
                'damage_type': damage_type,
                'image_url': image_url,
                'cooldown': None,  # 상세 페이지에서 추출 필요
                'mana_cost': None,  # 상세 페이지에서 추출 필요
            }

        except Exception as e:
            logger.error(f"Error parsing skill card: {e}")
            return None

    def _extract_tags(self, link_element, img_element) -> List[str]:
        """
        스킬 태그 추출

        태그는 이미지 alt, title, 또는 주변 span/div에서 추출 가능
        """
        tags = []

        # 이미지 alt 속성
        alt = img_element.get('alt', '')
        if alt:
            tags.append(alt)

        # title 속성
        title = link_element.get('title', '')
        if title:
            tags.extend(DataParser.parse_tags(title))

        # 주변 태그 엘리먼트 찾기 (예: <span class="tag">)
        parent = link_element.find_parent()
        if parent:
            tag_elements = parent.find_all(['span', 'div'], class_=['tag', 'label', 'badge'])
            for elem in tag_elements:
                tag_text = self.extract_text(elem)
                if tag_text:
                    tags.append(tag_text)

        return list(set(tags))  # 중복 제거

    def _infer_damage_type(self, tags: List[str]) -> Optional[str]:
        """태그에서 데미지 타입 추론"""
        damage_types = {
            'Physical', 'Fire', 'Cold', 'Lightning', 'Chaos',
            'Corrosion', 'Frost', 'Poison'
        }

        for tag in tags:
            for dtype in damage_types:
                if dtype.lower() in tag.lower():
                    return dtype

        return None

    def save_skills_to_db(self, skills_data: List[Dict], db: Session):
        """
        크롤링한 스킬 데이터를 데이터베이스에 저장

        Args:
            skills_data: 스킬 데이터 리스트
            db: 데이터베이스 세션
        """
        saved_count = 0

        for skill_data in skills_data:
            try:
                # 기존 스킬 확인
                existing_skill = db.query(Skill).filter(Skill.name == skill_data['name']).first()

                if existing_skill:
                    # 업데이트
                    existing_skill.type = skill_data.get('type', existing_skill.type)
                    existing_skill.description = skill_data.get('description', existing_skill.description)
                    existing_skill.tags = skill_data.get('tags', existing_skill.tags)
                    existing_skill.damage_type = skill_data.get('damage_type', existing_skill.damage_type)
                    existing_skill.image_url = skill_data.get('image_url', existing_skill.image_url)
                    logger.info(f"Updated skill: {skill_data['name']}")
                else:
                    # 새로 생성
                    new_skill = Skill(
                        name=skill_data['name'],
                        type=skill_data.get('type', ''),
                        description=skill_data.get('description', ''),
                        tags=skill_data.get('tags', '[]'),
                        damage_type=skill_data.get('damage_type'),
                        cooldown=skill_data.get('cooldown'),
                        mana_cost=skill_data.get('mana_cost'),
                        image_url=skill_data.get('image_url', '')
                    )
                    db.add(new_skill)
                    logger.info(f"Added new skill: {skill_data['name']}")

                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving skill {skill_data.get('name', 'Unknown')}: {e}")
                continue

        # 커밋
        db.commit()
        logger.info(f"Successfully saved {saved_count} skills to database")

    def export_to_json(self, skills_data: List[Dict], filename: str = "skills.json"):
        """스킬 데이터를 JSON 파일로 저장"""
        from pathlib import Path

        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(skills_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Skills data exported to: {filepath}")


def main():
    """스킬 크롤러 실행 메인 함수"""
    logger.info("Starting skills crawler...")

    with SkillsCrawler(delay=1.0) as crawler:
        # 1. 모든 카테고리의 스킬 크롤링
        skills_data = crawler.crawl_all_skills()

        if not skills_data:
            logger.warning("No skills data collected")
            return

        # 2. JSON으로 저장
        crawler.export_to_json(skills_data)

        # 3. 데이터베이스에 저장
        with get_db_session() as db:
            crawler.save_skills_to_db(skills_data, db)

    logger.info("Skills crawler finished!")


if __name__ == "__main__":
    main()
