#!/usr/bin/env python3
"""
스킬 페이지 HTML 구조 테스트
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.base_crawler import BaseCrawler

def test_skill_page():
    """스킬 페이지 HTML 구조 분석"""
    with BaseCrawler(delay=1.0) as crawler:
        soup = crawler.fetch_page("https://tlidb.com/en/Active_Skill")

        if not soup:
            print("Failed to fetch page")
            return

        # 스킬 이미지 찾기
        skill_images = soup.find_all('img', src=lambda x: x and 'Icon_Skill_' in x)
        print(f"✓ Found {len(skill_images)} skill images\n")

        # 첫 번째 스킬 상세 분석
        if skill_images:
            img = skill_images[0]
            print("=" * 70)
            print("첫 번째 스킬 분석:")
            print("=" * 70)

            # 이미지 URL
            print(f"\n이미지 URL: {img.get('src')}")

            # 부모 링크
            link = img.find_parent('a')
            if link:
                print(f"링크 href: {link.get('href')}")
                print(f"링크 텍스트: {link.get_text(strip=True)}")

            # 주변 요소 탐색
            print("\n=== 주변 HTML 구조 ===")

            # 링크 다음 형제 요소들
            if link:
                print("\n링크 다음 형제 요소들:")
                current = link.find_next_sibling()
                count = 0
                while current and count < 5:
                    if hasattr(current, 'name'):
                        print(f"  [{count}] <{current.name}> : {current.get_text(strip=True)[:100]}")
                    else:
                        text = str(current).strip()
                        if text:
                            print(f"  [{count}] [TEXT] : {text[:100]}")
                    current = current.find_next_sibling()
                    count += 1

            # 부모의 부모 (상위 컨테이너)
            if link:
                parent_container = link.find_parent()
                if parent_container:
                    print(f"\n부모 컨테이너: <{parent_container.name}>")
                    print(f"부모 클래스: {parent_container.get('class')}")

                    # 부모 내 모든 텍스트
                    all_text = parent_container.get_text(strip=True)
                    print(f"\n부모 내 전체 텍스트 (200자):\n{all_text[:200]}")

        # 두 번째 스킬도 확인
        if len(skill_images) > 1:
            print("\n\n" + "=" * 70)
            print("두 번째 스킬 분석:")
            print("=" * 70)

            img2 = skill_images[1]
            link2 = img2.find_parent('a')

            if link2:
                print(f"이미지: {img2.get('src', '')[-50:]}")
                print(f"링크: {link2.get('href')}")

                # 다음 형제들
                print("\n다음 형제 요소들:")
                current = link2.find_next_sibling()
                count = 0
                while current and count < 5:
                    if hasattr(current, 'name'):
                        print(f"  [{count}] <{current.name}>: {current.get_text(strip=True)[:80]}")
                    else:
                        text = str(current).strip()
                        if text:
                            print(f"  [{count}] [TEXT]: {text[:80]}")
                    current = current.find_next_sibling()
                    count += 1

if __name__ == "__main__":
    test_skill_page()
