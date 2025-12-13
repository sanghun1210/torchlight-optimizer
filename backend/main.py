"""
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import heroes, skills, items, talent_nodes, destinies, recommendations

# FastAPI 앱 생성
app = FastAPI(
    title="Torchlight Infinite Optimizer API",
    description="토치라이트 인피니트 최적 빌드 추천 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(heroes.router, prefix="/api/heroes", tags=["Heroes"])
app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])
app.include_router(talent_nodes.router, prefix="/api/talent-nodes", tags=["Talent Nodes"])
app.include_router(destinies.router, prefix="/api/destinies", tags=["Destinies"])
app.include_router(recommendations.router, prefix="/api/recommend", tags=["Recommendations"])


@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "Torchlight Infinite Optimizer API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "heroes": "/api/heroes",
            "skills": "/api/skills",
            "items": "/api/items",
            "talent_nodes": "/api/talent-nodes",
            "destinies": "/api/destinies",
            "recommendations": "/api/recommend"
        }
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
