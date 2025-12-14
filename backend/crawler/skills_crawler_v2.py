"""
스킬(Skills) 데이터 크롤러 v2 - 개별 페이지 크롤링
"""
import json
import logging
import re
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from backend.crawler.base_crawler import BaseCrawler, DataParser
from backend.database.models import Skill
from backend.database.db import get_db_session

logger = logging.getLogger(__name__)


class SkillsCrawlerV2(BaseCrawler):
    """스킬 데이터 크롤링 - 개별 페이지 방문"""

    # 스킬 카테고리 URL (한국어 페이지)
    SKILL_CATEGORIES = {
        'Active': 'https://tlidb.com/ko/Active_Skill',
        'Support': 'https://tlidb.com/ko/Support_Skill',
        'Passive': 'https://tlidb.com/ko/Passive_Skill',
        'Activation Medium': 'https://tlidb.com/ko/Activation_Medium_Skill',
        'Noble Support': 'https://tlidb.com/ko/Noble_Support_Skill',
        'Magnificent Support': 'https://tlidb.com/ko/Magnificent_Support_Skill',
    }

    def crawl_all_skills(self, detailed: bool = True) -> List[Dict]:
        """
        모든 카테고리의 스킬 크롤링

        Args:
            detailed: True면 개별 페이지 방문, False면 목록만

        Returns:
            스킬 정보 딕셔너리 리스트
        """
        all_skills = []

        for category, url in self.SKILL_CATEGORIES.items():
            logger.info(f"Crawling {category} skills from: {url}")
            skills = self.crawl_skills_by_category(url, category, detailed)
            all_skills.extend(skills)
            logger.info(f"Found {len(skills)} {category} skills")

        logger.info(f"Total skills found: {len(all_skills)}")
        return all_skills

    def crawl_skills_by_category(self, url: str, category: str, detailed: bool = True) -> List[Dict]:
        """
        특정 카테고리의 스킬 크롤링

        Args:
            url: 카테고리 페이지 URL
            category: 스킬 카테고리
            detailed: 개별 페이지 방문 여부

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
                href = link.get('href', '')
                skill_url = self.get_absolute_url(href)

                # 기본 정보
                skill_data = {
                    'name': self._extract_skill_name(link, img),
                    'type': category,
                    'url': skill_url,
                    'image_url': DataParser.extract_image_url(img, self.BASE_URL),
                }

                # 상세 정보 크롤링
                if detailed and skill_url:
                    details = self._fetch_skill_details(skill_url)
                    skill_data.update(details)

                skills.append(skill_data)
                logger.debug(f"Crawled skill: {skill_data.get('name', 'Unknown')}")

        # 중복 제거
        seen = set()
        unique_skills = []
        for skill in skills:
            skill_name = skill.get('name', '')
            if skill_name and skill_name not in seen:
                seen.add(skill_name)
                unique_skills.append(skill)

        return unique_skills

    def _extract_skill_name(self, link_element, img_element) -> str:
        """스킬 이름 추출"""
        # 링크 텍스트
        name = self.extract_text(link_element)

        if not name or name.startswith('http'):
            # 이미지 URL에서 추출
            img_url = img_element.get('src', '')
            if 'Icon_Skill_' in img_url:
                filename = img_url.split('/')[-1]
                name = filename.replace('Icon_Skill_', '').replace('_128.webp', '').replace('_', ' ')

        return name.strip()

    def _fetch_skill_details(self, skill_url: str) -> Dict:
        """
        개별 스킬 페이지에서 상세 정보 추출

        Args:
            skill_url: 스킬 상세 페이지 URL

        Returns:
            상세 정보 딕셔너리
        """
        details = {
            'tags': '[]',
            'description': '',
            'damage_type': None,
            'cooldown': None,
            'mana_cost': None,
        }

        soup = self.fetch_page(skill_url)
        if not soup:
            logger.warning(f"Failed to fetch skill details: {skill_url}")
            return details

        try:
            # 태그 추출
            # 태그들은 <span>으로 되어 있고, 부모는 class=['d-flex', 'flex-wrap', 'justify-content-center']
            tag_container = soup.find('div', class_='d-flex flex-wrap justify-content-center'.split())
            if not tag_container:
                # 다른 방법: Mobility 등의 span 찾기
                mobility_span = soup.find('span', string='Mobility')
                if mobility_span:
                    tag_container = mobility_span.parent

            if tag_container:
                # 모든 <span> 자식 추출
                tag_spans = tag_container.find_all('span')
                tags = [span.get_text(strip=True) for span in tag_spans if span.get_text(strip=True)]

                if tags:
                    details['tags'] = json.dumps(tags)

                    # 데미지 타입 추출
                    damage_types = {'Physical', 'Fire', 'Cold', 'Lightning', 'Erosion', 'Chaos'}
                    for tag in tags:
                        if tag in damage_types:
                            details['damage_type'] = tag
                            break

            # Mana Cost 추출
            mana_div = soup.find('div', string='Mana Cost')
            if mana_div:
                # 다음 형제에 값이 있음
                next_sib = mana_div.find_next_sibling()
                if next_sib:
                    mana_text = next_sib.get_text(strip=True)
                    try:
                        details['mana_cost'] = int(mana_text)
                    except ValueError:
                        # 숫자 추출 시도
                        mana_match = re.search(r'(\d+)', mana_text)
                        if mana_match:
                            details['mana_cost'] = int(mana_match.group(1))

            # Cast Speed / Cooldown 추출
            cast_div = soup.find('div', string='Cast Speed')
            if not cast_div:
                cast_div = soup.find('div', string='Cooldown')

            if cast_div:
                # 다음 형제에 값이 있음
                next_sib = cast_div.find_next_sibling()
                if next_sib:
                    time_text = next_sib.get_text(strip=True)
                    time_match = re.search(r'([\d.]+)\s*s', time_text)
                    if time_match:
                        details['cooldown'] = float(time_match.group(1))

            # 설명 추출 (전체 스킬 효과 정보 수집)
            description_parts = []

            # 1. Simple 섹션 찾기
            simple_div = soup.find('div', class_='detailsNote', string=lambda x: x and 'Simple' in str(x))
            if simple_div:
                parent = simple_div.parent
                if parent:
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        simple_text = next_elem.get_text(separator="\n", strip=True)
                        if simple_text and len(simple_text) > 10:
                            description_parts.append("=== Simple ===")
                            description_parts.append(simple_text)

            # 2. 다른 섹션들 찾기 (Details, Stats 등)
            # detailsNote 클래스를 가진 모든 div 탐색
            detail_notes = soup.find_all('div', class_='detailsNote')
            for note in detail_notes:
                note_text = note.get_text(strip=True)
                # Simple은 이미 처리했으므로 스킵
                if 'Simple' in note_text:
                    continue

                # 섹션 헤더로 사용
                parent = note.parent
                if parent:
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        section_text = next_elem.get_text(separator="\n", strip=True)
                        if section_text and len(section_text) > 10:
                            description_parts.append(f"=== {note_text} ===")
                            description_parts.append(section_text)

            # 3. card-header나 h3를 기준으로 추가 섹션 탐색
            headers = soup.find_all(['h3', 'div'], class_=lambda x: x and 'card-header' in str(x).lower())
            for header in headers[:3]:  # 최대 3개 섹션만
                header_text = header.get_text(strip=True)
                # 스킬 효과 관련 헤더 필터링
                if any(keyword in header_text.lower() for keyword in ['effect', 'skill', '효과', '수치', 'stat']):
                    # 헤더 다음에 오는 콘텐츠 추출
                    content_div = header.find_next_sibling()
                    if content_div:
                        content_text = content_div.get_text(separator="\n", strip=True)
                        if content_text and len(content_text) > 10:
                            description_parts.append(f"=== {header_text} ===")
                            description_parts.append(content_text)

            # 4. 모든 파트 결합
            if description_parts:
                details['description'] = "\n\n".join(description_parts)
            else:
                # fallback: 페이지 전체에서 주요 콘텐츠 영역 찾기
                main_content = soup.find('div', class_='container')
                if main_content:
                    fallback_text = main_content.get_text(separator="\n", strip=True)
                    # 너무 긴 경우 앞부분만
                    details['description'] = fallback_text[:2000] if fallback_text else ""

        except Exception as e:
            logger.error(f"Error parsing skill details from {skill_url}: {e}")

        return details

    def save_skills_to_db(self, skills_data: List[Dict], db: Session):
        """
        크롤링한 스킬 데이터를 데이터베이스에 저장
        """
        saved_count = 0

        for skill_data in skills_data:
            try:
                # url 필드 제거 (DB 모델에 없음)
                save_data = {k: v for k, v in skill_data.items() if k != 'url'}

                # 기존 스킬 확인
                existing_skill = db.query(Skill).filter(Skill.name == save_data['name']).first()

                if existing_skill:
                    # 업데이트
                    for key, value in save_data.items():
                        if hasattr(existing_skill, key):
                            setattr(existing_skill, key, value)
                    logger.info(f"Updated skill: {save_data['name']}")
                else:
                    # 새로 생성
                    new_skill = Skill(**save_data)
                    db.add(new_skill)
                    logger.info(f"Added new skill: {save_data['name']}")

                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving skill {skill_data.get('name', 'Unknown')}: {e}")
                continue

        # 커밋
        db.commit()
        logger.info(f"Successfully saved {saved_count} skills to database")

    def export_to_json(self, skills_data: List[Dict], filename: str = "skills_v2.json"):
        """스킬 데이터를 JSON 파일로 저장"""
        from pathlib import Path

        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(skills_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Skills data exported to: {filepath}")


def main():
    """스킬 크롤러 v2 실행 메인 함수"""
    logger.info("Starting skills crawler v2 (with detail pages)...")

    with SkillsCrawlerV2(delay=0.5) as crawler:  # 0.5초 딜레이로 빠르게
        # 1. 모든 카테고리의 스킬 크롤링 (상세 정보 포함)
        skills_data = crawler.crawl_all_skills(detailed=True)

        if not skills_data:
            logger.warning("No skills data collected")
            return

        # 2. JSON으로 저장
        crawler.export_to_json(skills_data)

        # 3. 데이터베이스에 저장
        with get_db_session() as db:
            crawler.save_skills_to_db(skills_data, db)

    logger.info("Skills crawler v2 finished!")


if __name__ == "__main__":
    main()
