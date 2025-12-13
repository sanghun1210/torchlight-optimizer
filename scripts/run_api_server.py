#!/usr/bin/env python3
"""
FastAPI 서버 실행 스크립트
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("Torchlight Infinite Optimizer API 서버 시작")
    print("=" * 70)
    print()
    print("API 문서: http://localhost:8000/docs")
    print("API 루트: http://localhost:8000")
    print()
    print("종료: Ctrl+C")
    print("=" * 70)

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 개발 모드: 코드 변경 시 자동 재시작
        log_level="info"
    )
