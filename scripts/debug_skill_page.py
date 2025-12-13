#!/usr/bin/env python3
"""
스킬 상세 페이지 HTML 구조 디버깅
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.base_crawler import BaseCrawler

def debug_skill_page():
    """스킬 페이지 HTML 구조 출력"""
    with BaseCrawler(delay=0.5) as crawler:
        url = "https://tlidb.com/Leap_Attack"
        print(f"Fetching: {url}\n")

        soup = crawler.fetch_page(url)
        if not soup:
            print("Failed to fetch page")
            return

        print("=" * 70)
        print("전체 페이지 텍스트 (처음 1000자)")
        print("=" * 70)
        all_text = soup.get_text(separator=' ', strip=True)
        print(all_text[:1000])
        print("\n")

        print("=" * 70)
        print("스킬 아이콘 이미지 찾기")
        print("=" * 70)
        skill_icons = soup.find_all('img', src=lambda x: x and 'Icon_Skill_' in x)
        print(f"Found {len(skill_icons)} skill icons")

        if skill_icons:
            icon = skill_icons[0]
            print(f"Icon src: {icon.get('src', '')}")

            # 아이콘 주변 구조 출력
            print("\n아이콘 다음 10개 형제 요소:")
            current = icon
            for i in range(10):
                current = current.find_next_sibling()
                if not current:
                    break
                if hasattr(current, 'name'):
                    text = current.get_text(strip=True)
                    print(f"  [{i}] <{current.name}> class={current.get('class')} : {text[:80]}")
                else:
                    text = str(current).strip()
                    if text:
                        print(f"  [{i}] [TEXT] : {text[:80]}")

        print("\n" + "=" * 70)
        print("특정 키워드 검색")
        print("=" * 70)

        # Mana Cost 찾기
        mana_elements = soup.find_all(string=lambda x: x and 'Mana Cost' in str(x))
        print(f"\n'Mana Cost' 포함 요소: {len(mana_elements)}개")
        for elem in mana_elements[:3]:
            parent = elem.find_parent()
            if parent:
                print(f"  - {parent.name}: {parent.get_text(strip=True)[:100]}")

        # Cast Speed 찾기
        cast_elements = soup.find_all(string=lambda x: x and ('Cast Speed' in str(x) or 'Cooldown' in str(x)))
        print(f"\n'Cast Speed/Cooldown' 포함 요소: {len(cast_elements)}개")
        for elem in cast_elements[:3]:
            parent = elem.find_parent()
            if parent:
                print(f"  - {parent.name}: {parent.get_text(strip=True)[:100]}")

        # Mobility, Attack 등 태그 키워드
        tag_keywords = ['Mobility', 'Attack', 'Melee', 'Physical', 'Strength']
        for keyword in tag_keywords:
            elements = soup.find_all(string=lambda x: x and keyword in str(x))
            if elements:
                print(f"\n'{keyword}' 포함 요소: {len(elements)}개")
                elem = elements[0]
                parent = elem.find_parent() if hasattr(elem, 'find_parent') else None
                if parent:
                    print(f"  - {parent.name}: {parent.get_text(strip=True)[:100]}")

if __name__ == "__main__":
    debug_skill_page()
