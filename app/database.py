from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Функция-зависимость для получения сессии базы данных.
    Возвращает сессию БД и гарантирует ее закрытие после использования.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

