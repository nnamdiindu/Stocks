from datetime import datetime, timezone
from flask_login import UserMixin
from sqlalchemy import String, Boolean, DateTime, Integer, Enum, func, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app import db


class AccountStatus(enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"
    PENDING_VERIFICATION = "pending_verification"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20))
    date_of_birth: Mapped[Date] = mapped_column(Date)

    # Account status
    account_status: Mapped[str] = mapped_column(Enum(AccountStatus), default=AccountStatus.PENDING_VERIFICATION, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # KYC/Verification
    id_document_type: Mapped[str] = mapped_column(String(50), nullable=True)
    id_document_number: Mapped[str] = mapped_column(String(100), nullable=True)
    verification_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    last_login: Mapped[datetime] = mapped_column(default=func.now())


    # Relationships
    # account = relationship("UserAccount", back_populates="user", uselist=False)
    # holdings = relationship("UserHolding", back_populates="user", cascade="all, delete-orphan")
    # stock_transactions = relationship("StockTransaction", back_populates="user", cascade="all, delete-orphan")
    # deposits = relationship("Deposit", back_populates="user", cascade="all, delete-orphan")
    # withdrawals = relationship("Withdrawal", back_populates="user", cascade="all, delete-orphan")
    # transaction_history = relationship("TransactionHistory", back_populates="user", cascade="all, delete-orphan")
    # notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    # Referral relationships
    # referred_by = relationship("User", remote_side=[user_id], backref="referrals")
    # referral_given = relationship("Referral", foreign_keys="Referral.referrer_id", back_populates="referrer")
    # referral_received = relationship("Referral", foreign_keys="Referral.referred_id", back_populates="referred_user",
    #                                  uselist=False)
    # rewards_earned = relationship("ReferralReward", foreign_keys="ReferralReward.user_id", back_populates="user")

    def __repr__(self):
        return f"<User(user_id={self.id}, username='{self.username}', email='{self.email}')>"