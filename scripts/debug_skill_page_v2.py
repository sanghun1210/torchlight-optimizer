#!/usr/bin/env python3
"""
스킬 상세 페이지 HTML 구조 상세 분석
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.base_crawler import BaseCrawler

def analyze_skill_structure():
    """스킬 페이지 구조 상세 분석"""
    with BaseCrawler(delay=0.5) as crawler:
        url = "https://tlidb.com/Leap_Attack"
        soup = crawler.fetch_page(url)

        if not soup:
            print("Failed to fetch page")
            return

        print("=" * 70)
        print("태그 분석 (Mobility, Attack, Melee 등)")
        print("=" * 70)

        # 태그들은 <span>으로 되어 있음
        mobility_span = soup.find('span', string='Mobility')
        if mobility_span:
            print(f"Mobility span 찾음!")
            print(f"  부모: <{mobility_span.parent.name}> class={mobility_span.parent.get('class')}")

            # 부모의 모든 자식 확인
            parent = mobility_span.parent
            print(f"\n부모의 모든 텍스트:")
            print(f"  {parent.get_text(strip=True)}")

            print(f"\n부모의 모든 <span> 자식:")
            spans = parent.find_all('span')
            tags = [span.get_text(strip=True) for span in spans]
            print(f"  태그들: {tags}")

        print("\n" + "=" * 70)
        print("Mana Cost 분석")
        print("=" * 70)

        mana_div = soup.find('div', string='Mana Cost')
        if mana_div:
            print(f"Mana Cost div 찾음!")
            print(f"  부모: <{mana_div.parent.name}> class={mana_div.parent.get('class')}")

            # 다음 형제 확인
            next_sib = mana_div.find_next_sibling()
            if next_sib:
                print(f"  다음 형제: <{next_sib.name}> : {next_sib.get_text(strip=True)}")

            # 부모의 텍스트
            parent = mana_div.parent
            print(f"  부모 텍스트: {parent.get_text(strip=True)}")

        print("\n" + "=" * 70)
        print("Cast Speed 분석")
        print("=" * 70)

        cast_div = soup.find('div', string='Cast Speed')
        if cast_div:
            print(f"Cast Speed div 찾음!")

            # 다음 형제 확인
            next_sib = cast_div.find_next_sibling()
            if next_sib:
                print(f"  다음 형제: <{next_sib.name}> : {next_sib.get_text(strip=True)}")

            # 부모의 텍스트
            parent = cast_div.parent
            print(f"  부모 텍스트: {parent.get_text(strip=True)}")

        print("\n" + "=" * 70)
        print("Main Stat 분석")
        print("=" * 70)

        # Main Stat 찾기
        main_stat_elements = soup.find_all(string=lambda x: x and 'Main Stat' in str(x))
        if main_stat_elements:
            print(f"'Main Stat' 포함 요소 찾음!")
            for elem in main_stat_elements[:1]:
                parent = elem.find_parent() if hasattr(elem, 'find_parent') else None
                if parent:
                    print(f"  부모: <{parent.name}> : {parent.get_text(strip=True)}")

        print("\n" + "=" * 70)
        print("설명 (Simple/Details) 분석")
        print("=" * 70)

        simple_elements = soup.find_all(string=lambda x: x and 'Simple' in str(x))
        if simple_elements:
            print(f"'Simple' 포함 요소: {len(simple_elements)}개")
            elem = simple_elements[0]
            parent = elem.find_parent() if hasattr(elem, 'find_parent') else None
            if parent:
                print(f"  부모: <{parent.name}> class={parent.get('class')}")
                print(f"  텍스트: {parent.get_text(strip=True)[:100]}")

                # 다음 형제
                next_elem = parent.find_next_sibling()
                if next_elem:
                    print(f"\n  다음 형제: <{next_elem.name}> class={next_elem.get('class')}")
                    print(f"  텍스트: {next_elem.get_text(strip=True)[:200]}")

if __name__ == "__main__":
    analyze_skill_structure()
