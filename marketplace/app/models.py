from sqlalchemy import Column, String, Float, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from app.config import settings

engine = None
SessionLocal = None
Base = declarative_base()


def init_db(db_url=None):
    """Initialize database engine and session."""
    global engine, SessionLocal
    from sqlalchemy import create_engine
    url = db_url or settings.db_url
    engine = create_engine(url, connect_args={"check_same_thread": False} if "sqlite" in url else {})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return engine, SessionLocal


# Always initialize when module is loaded
engine, SessionLocal = init_db()


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="client")  # client, manager, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payments = relationship("Payment", back_populates="user")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    client_name = Column(String(200), nullable=False)
    property_name = Column(String(300))
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), default="mpesa")
    mpesa_phone = Column(String(20))
    mpesa_till_number = Column(String(50))
    mpesa_receipt_number = Column(String(100))
    status = Column(String(20), default="pending")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    reminder_sent = Column(Boolean, default=False)

    user = relationship("User", back_populates="payments")
