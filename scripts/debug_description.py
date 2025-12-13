#!/usr/bin/env python3
"""
설명(Description) HTML 구조 상세 분석
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.base_crawler import BaseCrawler

def analyze_description():
    """설명 영역 HTML 구조 상세 분석"""
    with BaseCrawler(delay=0.5) as crawler:
        url = "https://tlidb.com/Leap_Attack"
        soup = crawler.fetch_page(url)

        if not soup:
            print("Failed to fetch page")
            return

        print("=" * 70)
        print("'Simple' 텍스트 주변 구조 분석")
        print("=" * 70)

        # Simple 포함 요소 찾기
        simple_elements = soup.find_all(string=lambda x: x and 'Simple' in str(x))

        for i, elem in enumerate(simple_elements):
            print(f"\n[{i+1}] Simple 요소:")
            print(f"  타입: {type(elem)}")
            print(f"  내용: '{elem}'")

            # 부모 확인
            parent = elem.find_parent() if hasattr(elem, 'find_parent') else None
            if parent:
                print(f"  부모: <{parent.name}> class={parent.get('class')}")

                # 부모의 다음 형제
                next_sib = parent.find_next_sibling()
                if next_sib:
                    print(f"  부모의 다음 형제: <{next_sib.name}> class={next_sib.get('class')}")
                    desc = next_sib.get_text(strip=True)
                    print(f"  텍스트 (처음 200자): {desc[:200]}")
                else:
                    print(f"  부모의 다음 형제: None")

                # 부모의 부모 확인
                grandparent = parent.parent
                if grandparent:
                    print(f"  조부모: <{grandparent.name}> class={grandparent.get('class')}")

                    # 조부모의 다음 형제
                    grand_next = grandparent.find_next_sibling()
                    if grand_next:
                        print(f"  조부모의 다음 형제: <{grand_next.name}> class={grand_next.get('class')}")
                        desc = grand_next.get_text(strip=True)
                        print(f"  텍스트 (처음 200자): {desc[:200]}")

                # 부모의 모든 자식 출력
                print(f"\n  부모의 모든 자식:")
                for j, child in enumerate(parent.children):
                    if hasattr(child, 'name') and child.name:
                        print(f"    [{j}] <{child.name}> : {child.get_text(strip=True)[:50]}")
                    else:
                        text = str(child).strip()
                        if text:
                            print(f"    [{j}] [TEXT] : {text[:50]}")

        print("\n" + "=" * 70)
        print("class='detailsNote' 요소 모두 찾기")
        print("=" * 70)

        details_notes = soup.find_all('div', class_='detailsNote')
        for i, note in enumerate(details_notes):
            print(f"\n[{i+1}] detailsNote div:")
            print(f"  텍스트: {note.get_text(strip=True)}")

            # 다음 형제
            next_sib = note.find_next_sibling()
            if next_sib:
                print(f"  다음 형제: <{next_sib.name}> class={next_sib.get('class')}")
                desc = next_sib.get_text(strip=True)
                print(f"  텍스트 (처음 300자): {desc[:300]}")

if __name__ == "__main__":
    analyze_description()
