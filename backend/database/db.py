"""
데이터베이스 연결 및 세션 관리
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from backend.database.models import Base


# 프로젝트 루트 디렉토리
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"

# 데이터 디렉토리 생성
DATA_DIR.mkdir(exist_ok=True)

# 데이터베이스 파일 경로
DATABASE_URL = f"sqlite:///{DATA_DIR}/torchlight.db"

# SQLite 엔진 생성
# check_same_thread=False: FastAPI에서 멀티스레드 사용 가능하게
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False  # True로 설정하면 SQL 쿼리 로그 출력
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database tables created at: {DATA_DIR}/torchlight.db")


def drop_tables():
    """데이터베이스 테이블 삭제 (주의: 모든 데이터 삭제됨)"""
    Base.metadata.drop_all(bind=engine)
    print("✗ All database tables dropped")


def get_db() -> Session:
    """
    데이터베이스 세션 생성 (FastAPI dependency용)

    Usage:
        @app.get("/")
        def read_root(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    데이터베이스 세션 생성 (일반 스크립트용)

    Usage:
        with get_db_session() as db:
            heroes = db.query(Hero).all()
    """
    return SessionLocal()


if __name__ == "__main__":
    # 테이블 생성 테스트
    print(f"Database URL: {DATABASE_URL}")
    create_tables()

    # 테이블 확인
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nCreated tables ({len(tables)}):")
    for table in tables:
        print(f"  - {table}")
