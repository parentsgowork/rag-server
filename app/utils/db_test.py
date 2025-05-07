from sqlalchemy import text
from app.core.db import SessionLocal


def test_connection():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        print("✅ DB 연결 성공")
    except Exception as e:
        print("❌ DB 연결 실패:", e)
    finally:
        db.close()


if __name__ == "__main__":
    test_connection()
