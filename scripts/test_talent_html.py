#!/usr/bin/env python3
"""
재능 페이지 HTML 구조 확인 스크립트
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
from bs4 import BeautifulSoup


def analyze_talent_page():
    """Anger 페이지의 HTML 구조 분석"""
    url = "https://tlidb.com/en/Anger"

    print("=" * 80)
    print(f"Fetching: {url}")
    print("=" * 80)

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # 1. 모든 card-body 찾기
    print("\n[1] Searching for card-body elements...")
    card_bodies = soup.find_all('div', class_='card-body')
    print(f"Found {len(card_bodies)} card-body elements\n")

    for i, card in enumerate(card_bodies[:3], 1):  # 처음 3개만
        print(f"Card {i}:")
        text = card.get_text(strip=True)[:200]
        print(f"  Text: {text}...\n")

    # 2. "Require lv" 패턴 찾기
    print("\n[2] Searching for 'Require lv' pattern...")
    require_lv_elements = soup.find_all(string=lambda x: x and 'Require lv' in x)
    print(f"Found {len(require_lv_elements)} elements with 'Require lv'\n")

    for i, elem in enumerate(require_lv_elements[:5], 1):
        print(f"Element {i}: {elem.strip()}")
        if elem.parent:
            print(f"  Parent tag: <{elem.parent.name}>")
            print(f"  Parent class: {elem.parent.get('class', 'None')}")
        print()

    # 3. "Tunnel Vision" 찾기
    print("\n[3] Searching for 'Tunnel Vision'...")
    tunnel_elements = soup.find_all(string=lambda x: x and 'Tunnel Vision' in x)
    print(f"Found {len(tunnel_elements)} elements with 'Tunnel Vision'\n")

    for i, elem in enumerate(tunnel_elements, 1):
        print(f"Element {i}:")
        if elem.parent:
            # 부모 요소의 HTML 출력
            parent_html = str(elem.parent)[:300]
            print(f"  Parent HTML: {parent_html}...\n")

    # 4. 모든 h3, h4, h5 태그 찾기
    print("\n[4] Searching for headers (h3, h4, h5)...")
    headers = soup.find_all(['h3', 'h4', 'h5'])
    print(f"Found {len(headers)} headers\n")

    for i, header in enumerate(headers[:10], 1):
        print(f"Header {i}: <{header.name}> {header.get_text(strip=True)[:100]}")

    # 5. 전체 구조 샘플 (처음 2000자)
    print("\n" + "=" * 80)
    print("[5] Full HTML Sample (first 2000 chars):")
    print("=" * 80)
    print(soup.prettify()[:2000])


if __name__ == "__main__":
    try:
        analyze_talent_page()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
