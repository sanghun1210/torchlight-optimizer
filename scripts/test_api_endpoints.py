#!/usr/bin/env python3
"""
API 엔드포인트 테스트 스크립트
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_endpoint(name: str, url: str):
    """API 엔드포인트 테스트"""
    print(f"\n[테스트] {name}")
    print(f"URL: {url}")
    print("-" * 70)

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()

        # 결과 출력
        if isinstance(data, list):
            print(f"✓ 성공: {len(data)}개 항목")
            if data:
                print(f"첫 번째 항목: {json.dumps(data[0], ensure_ascii=False, indent=2)[:200]}...")
        elif isinstance(data, dict):
            print(f"✓ 성공")
            print(f"응답: {json.dumps(data, ensure_ascii=False, indent=2)[:300]}...")

        return True

    except requests.exceptions.RequestException as e:
        print(f"✗ 실패: {e}")
        return False


def main():
    """모든 API 엔드포인트 테스트"""
    print("=" * 70)
    print("Torchlight Infinite API 엔드포인트 테스트")
    print("=" * 70)
    print("\n⚠ 주의: API 서버가 실행 중이어야 합니다 (http://localhost:8000)")

    # 서버 연결 확인
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✓ API 서버 연결 확인")
        else:
            print("✗ API 서버 응답 오류")
            return
    except requests.exceptions.RequestException:
        print("✗ API 서버에 연결할 수 없습니다. 서버를 먼저 실행하세요:")
        print("  python scripts/run_api_server.py")
        return

    # 각 엔드포인트 테스트
    tests = [
        ("루트 엔드포인트", f"{BASE_URL}/"),
        ("헬스 체크", f"{BASE_URL}/health"),
        ("영웅 목록", f"{BASE_URL}/api/heroes?limit=3"),
        ("영웅 God 타입 목록", f"{BASE_URL}/api/heroes/god-types/list"),
        ("스킬 목록", f"{BASE_URL}/api/skills?limit=3"),
        ("스킬 타입 목록", f"{BASE_URL}/api/skills/types/list"),
        ("스킬 데미지 타입 목록", f"{BASE_URL}/api/skills/damage-types/list"),
        ("아이템 목록", f"{BASE_URL}/api/items?limit=3"),
        ("아이템 타입 목록", f"{BASE_URL}/api/items/types/list"),
        ("아이템 슬롯 목록", f"{BASE_URL}/api/items/slots/list"),
        ("재능 노드 목록", f"{BASE_URL}/api/talent-nodes?limit=3"),
        ("재능 노드 타입 목록", f"{BASE_URL}/api/talent-nodes/types/list"),
        ("운명 목록", f"{BASE_URL}/api/destinies?limit=3"),
        ("운명 티어 목록", f"{BASE_URL}/api/destinies/tiers/list"),
    ]

    success_count = 0
    for name, url in tests:
        if test_endpoint(name, url):
            success_count += 1

    # 최종 결과
    print("\n" + "=" * 70)
    print(f"테스트 완료: {success_count}/{len(tests)} 성공")
    print("=" * 70)

    if success_count == len(tests):
        print("✓ 모든 API 엔드포인트가 정상 작동합니다!")
    else:
        print(f"⚠ {len(tests) - success_count}개 엔드포인트에서 오류가 발생했습니다.")


if __name__ == "__main__":
    main()
