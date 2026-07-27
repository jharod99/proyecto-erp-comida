from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./inventario_jugueria.db"

# connect_args={"check_same_thread": False} es necesario para SQLite en FastAPI
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Inyector de dependencia para obtener la sesión de BD por request en FastAPI.
    Garantiza el cierre automático de la conexión.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
