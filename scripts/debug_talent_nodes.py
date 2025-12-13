#!/usr/bin/env python3
"""
재능 노드(Talent Nodes) 페이지 HTML 구조 분석
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.base_crawler import BaseCrawler

def analyze_talent_nodes():
    """재능 노드 페이지 구조 분석"""
    with BaseCrawler(delay=0.5) as crawler:
        url = "https://tlidb.com/en/Talent"

        print("=" * 70)
        print(f"재능 노드 페이지 분석: {url}")
        print("=" * 70)

        soup = crawler.fetch_page(url)
        if not soup:
            print("Failed to fetch page")
            return

        # 페이지 전체 텍스트 (처음 2000자)
        print("\n페이지 텍스트 (처음 2000자):")
        print("-" * 70)
        all_text = soup.get_text(separator=' ', strip=True)
        print(all_text[:2000])

        # 'Core' 키워드 검색
        print("\n" + "=" * 70)
        print("'Core' 키워드 검색 (코어 재능 노드)")
        print("=" * 70)
        core_elements = soup.find_all(string=lambda x: x and 'Core' in str(x))
        print(f"Found {len(core_elements)} 'Core' elements")
        for i, elem in enumerate(core_elements[:5]):
            text = str(elem).strip()
            if len(text) < 100:
                print(f"  [{i}] '{text}'")
                parent = elem.find_parent() if hasattr(elem, 'find_parent') else None
                if parent:
                    print(f"      부모: <{parent.name}> class={parent.get('class')}")

        # 'Talent' 키워드 검색
        print("\n" + "=" * 70)
        print("'Talent' 키워드 검색")
        print("=" * 70)
        talent_elements = soup.find_all(string=lambda x: x and 'Talent' in str(x) and 'Core' not in str(x))
        print(f"Found {len(talent_elements)} 'Talent' elements (without Core)")
        for i, elem in enumerate(talent_elements[:5]):
            text = str(elem).strip()
            if len(text) < 100:
                print(f"  [{i}] '{text}'")

        # 이미지 검색 (재능 노드 아이콘)
        print("\n" + "=" * 70)
        print("재능 노드 이미지 검색")
        print("=" * 70)

        # 다양한 패턴으로 재능 노드 이미지 찾기
        patterns = ['Talent', 'Icon', 'Node', 'Skill']
        for pattern in patterns:
            images = soup.find_all('img', src=lambda x: x and pattern in x)
            if images:
                print(f"\n'{pattern}' 패턴 이미지: {len(images)}개")
                for i, img in enumerate(images[:3]):
                    src = img.get('src', '')
                    print(f"  [{i}] {src[-80:]}")

        # 링크 검색
        print("\n" + "=" * 70)
        print("재능 관련 링크 검색")
        print("=" * 70)
        links = soup.find_all('a', href=True)
        talent_links = [link for link in links if 'talent' in link.get('href', '').lower()]
        print(f"Found {len(talent_links)} talent-related links")
        for i, link in enumerate(talent_links[:10]):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"  [{i}] href={href}, text={text[:50]}")

        # 특정 클래스 검색
        print("\n" + "=" * 70)
        print("카드/컨테이너 구조 검색")
        print("=" * 70)

        # card 클래스
        cards = soup.find_all('div', class_=lambda x: x and 'card' in str(x).lower())
        print(f"Card 클래스: {len(cards)}개")

        # border 클래스
        borders = soup.find_all('div', class_=lambda x: x and 'border' in str(x).lower())
        print(f"Border 클래스: {len(borders)}개")

if __name__ == "__main__":
    analyze_talent_nodes()
