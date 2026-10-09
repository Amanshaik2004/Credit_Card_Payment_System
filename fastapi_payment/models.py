from datetime import datetime, timezone
from sqlalchemy import Column, BigInteger, Integer, String, Numeric, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

def utc_now():
    return datetime.now(timezone.utc)

def AutoPK():
    return Column(BigInteger().with_variant(Integer, 'sqlite'), primary_key=True, autoincrement=True, index=True)

class User(Base):
    __tablename__ = 'users'

    id = AutoPK()
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(150), default='')
    last_name = Column(String(150), default='')
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    date_joined = Column(DateTime, default=utc_now)

    cards = relationship('Card', back_populates='user')
    transactions = relationship('Transaction', back_populates='user')


class Card(Base):
    __tablename__ = 'cards'

    id = AutoPK()
    user_id = Column(BigInteger().with_variant(Integer, 'sqlite'), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    card_holder_name = Column(String(100), nullable=False)
    card_type = Column(String(20), nullable=False, default='CREDIT')
    card_brand = Column(String(30), nullable=False, default='Visa')
    masked_card_number = Column(String(30), nullable=False)
    last_4_digits = Column(String(4), nullable=False)
    expiry_month = Column(Integer, nullable=False)
    expiry_year = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship('User', back_populates='cards')
    transactions = relationship('Transaction', back_populates='card')


class Transaction(Base):
    __tablename__ = 'transactions'

    id = AutoPK()
    transaction_id = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(BigInteger().with_variant(Integer, 'sqlite'), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    card_id = Column(BigInteger().with_variant(Integer, 'sqlite'), ForeignKey('cards.id', ondelete='RESTRICT'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default='USD')
    status = Column(String(20), default='PENDING', nullable=False)  # PENDING, SUCCESS, FAILED
    description = Column(String(255), default='')
    failure_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship('User', back_populates='transactions')
    card = relationship('Card', back_populates='transactions')


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = AutoPK()
    user_id = Column(BigInteger().with_variant(Integer, 'sqlite'), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = Column(String(100), nullable=False)
    ip_address = Column(String(45), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
