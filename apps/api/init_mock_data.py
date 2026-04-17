from database import Base, SessionLocal, engine
from schema import ensure_database_schema
from seed_demo_data import ensure_demo_data
from services.rag_service import ensure_library_vectorized


def main() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_database_schema()
    vectorized_books = 0
    db = SessionLocal()
    try:
        stats = ensure_demo_data(db, force=True)
        try:
            vectorized_books = ensure_library_vectorized(db, force=True)
        except Exception as exc:
            print(f"向量化暂时跳过: {exc}")
    finally:
        db.close()

    print("示例数据已重建完成")
    print(f"书籍数: {stats['books']}")
    print(f"章节数: {stats['chapters']}")
    print(f"书架数: {stats['bookshelf']}")
    print(f"已向量化书籍数: {vectorized_books}")


if __name__ == "__main__":
    main()
