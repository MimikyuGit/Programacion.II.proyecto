from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

RUTA_BD = Path(__file__).resolve().parent / "estacionamiento.db"
DATABASE_URL = f"sqlite:///{RUTA_BD}"

engine = create_engine(DATABASE_URL)
@event.listens_for(engine, "connect")
def activar_claves_foraneas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

Base = declarative_base()

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)


def inicializar_bd():
    from database import modelos

    Base.metadata.create_all(bind=engine)
