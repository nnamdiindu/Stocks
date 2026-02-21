from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlalchemy import String, Text, Boolean, DateTime, JSON, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import db


class NotificationType(str, Enum):
    """Notification type/severity levels"""
    SUCCESS = 'success'
    WARNING = 'warning'
    INFO = 'info'
    DANGER = 'danger'


class NotificationCategory(str, Enum):
    """Notification categories for grouping and filtering"""
    TRADE = 'trade'
    WALLET = 'wallet'
    SECURITY = 'security'
    KYC = 'kyc'
    SYSTEM = 'system'
    PROMOTION = 'promotion'
    ACCOUNT = 'account'


class NotificationPriority(str, Enum):
    """Priority levels for notification ordering and display"""
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    URGENT = 'urgent'


class Notification(db.Model):
    """Main notification model"""
    __tablename__ = 'notifications'

    # Primary Fields
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)

    # Notification Content
    type: Mapped[str] = mapped_column(String(20), default=NotificationType.INFO.value)
    category: Mapped[str] = mapped_column(String(50), default=NotificationCategory.SYSTEM.value)
    priority: Mapped[str] = mapped_column(String(20), default=NotificationPriority.NORMAL.value)
    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)

    # Action Fields
    action_text: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    action_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Status Tracking
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Metadata & Context
    notification_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    related_object_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    related_object_id: Mapped[Optional[int]] = mapped_column(nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Email/Push Notification Tracking
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    email_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    push_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    push_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="notifications")

    @classmethod
    def create_trade_notification(cls, session, user_id: int, trade_data: dict):
        """
        Factory method for trade-related notifications.

        A classmethod receives the class itself (cls) as first argument instead of
        an instance (self). This means you call it on the class directly:
        Notification.create_trade_notification(...) — not on an object instance.
        """
        action = trade_data.get("action", "executed").capitalize()
        symbol = trade_data.get("symbol", "Unknown")
        quantity = trade_data.get("quantity", 0)
        price = trade_data.get("price", 0)
        trade_id = trade_data.get("trade_id")

        notification = cls(
            user_id=user_id,
            type=NotificationType.SUCCESS.value,
            category=NotificationCategory.TRADE.value,
            priority=NotificationPriority.HIGH.value,
            title=f"Trade Executed: {action} {symbol}",
            message=f"You {action.lower()}t {quantity} share{'s' if quantity != 1 else ''} of {symbol} at ${price:,.2f}",
            action_text="View Trade",
            action_url=f"/dashboard/trades/{trade_id}" if trade_id else "/dashboard/trades",
            notification_metadata={
                "trade_id": trade_id,
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "action": action.lower()
            }
        )
        session.add(notification)
        session.commit()
        return notification

    @classmethod
    def create_wallet_notification(cls, session, user_id: int, wallet_data: dict, notification_type: str = "deposit"):
        """
        Factory method for wallet/payment notifications.
        notification_type: 'deposit', 'withdrawal', 'pending', 'failed'
        """
        amount = wallet_data.get("amount", 0)
        method = wallet_data.get("method", "crypto")
        transaction_id = wallet_data.get("transaction_id")

        config = {
            "deposit": {
                "type": NotificationType.SUCCESS.value,
                "title": "Deposit Successful",
                "message": f"Your deposit of ${amount:,.2f} via {method} has been confirmed.",
            },
            "withdrawal": {
                "type": NotificationType.SUCCESS.value,
                "title": "Withdrawal Processed",
                "message": f"Your withdrawal of ${amount:,.2f} via {method} is being processed.",
            },
            "pending": {
                "type": NotificationType.WARNING.value,
                "title": "Transaction Pending",
                "message": f"Your transaction of ${amount:,.2f} is awaiting confirmation.",
            },
            "failed": {
                "type": NotificationType.DANGER.value,
                "title": "Transaction Failed",
                "message": f"Your transaction of ${amount:,.2f} via {method} could not be completed.",
            },
        }

        cfg = config.get(notification_type, config["deposit"])

        notification = cls(
            user_id=user_id,
            type=cfg["type"],
            category=NotificationCategory.WALLET.value,
            priority=NotificationPriority.HIGH.value,
            title=cfg["title"],
            message=cfg["message"],
            action_text="View Wallet",
            action_url="/dashboard/wallet",
            notification_metadata={
                "transaction_id": transaction_id,
                "amount": amount,
                "method": method,
                "notification_type": notification_type
            }
        )
        session.add(notification)
        session.commit()
        return notification

    @classmethod
    def create_security_notification(cls, session, user_id: int, security_data: dict):
        """
        Factory method for security alerts — always urgent priority.
        """
        title = security_data.get("title", "Security Alert")
        message = security_data.get("message", "A security event was detected on your account.")

        notification = cls(
            user_id=user_id,
            type=NotificationType.WARNING.value,
            category=NotificationCategory.SECURITY.value,
            priority=NotificationPriority.URGENT.value,
            title=title,
            message=message,
            action_text="Review Activity",
            action_url="/dashboard/security",
            notification_metadata={
                "ip_address": security_data.get("ip_address"),
                "location": security_data.get("location"),
                "device": security_data.get("device"),
            }
        )
        session.add(notification)
        session.commit()
        return notification

    @classmethod
    def create_kyc_notification(cls, session, user_id: int, kyc_status: str):
        """
        Factory method for KYC status notifications.
        kyc_status: 'pending', 'approved', 'rejected', 'additional_docs'
        """
        config = {
            "pending": {
                "type": NotificationType.INFO.value,
                "title": "KYC Verification Submitted",
                "message": "Your identity documents have been submitted and are under review. This usually takes 1-2 business days.",
                "priority": NotificationPriority.NORMAL.value,
            },
            "approved": {
                "type": NotificationType.SUCCESS.value,
                "title": "KYC Verification Approved",
                "message": "Your identity has been verified. You now have full access to all StocksCo features.",
                "priority": NotificationPriority.HIGH.value,
            },
            "rejected": {
                "type": NotificationType.DANGER.value,
                "title": "KYC Verification Failed",
                "message": "Your verification was unsuccessful. Please re-submit with valid documents.",
                "priority": NotificationPriority.URGENT.value,
            },
            "additional_docs": {
                "type": NotificationType.WARNING.value,
                "title": "Additional Documents Required",
                "message": "We need additional documents to complete your verification. Please check your KYC dashboard.",
                "priority": NotificationPriority.HIGH.value,
            },
        }

        cfg = config.get(kyc_status, config["pending"])

        notification = cls(
            user_id=user_id,
            type=cfg["type"],
            category=NotificationCategory.KYC.value,
            priority=cfg["priority"],
            title=cfg["title"],
            message=cfg["message"],
            action_text="Go to KYC",
            action_url="/dashboard/kyc",
            notification_metadata={"kyc_status": kyc_status}
        )
        session.add(notification)
        session.commit()
        return notification

    # Composite Indexes
    __table_args__ = (
        Index('idx_user_read_created', 'user_id', 'is_read', 'created_at'),
        Index('idx_user_category', 'user_id', 'category'),
        Index('idx_expires_deleted', 'expires_at', 'deleted_at'),
    )

    def __repr__(self) -> str:
        return f'<Notification {self.id}: {self.title} for User {self.user_id}>'

    def to_dict(self) -> dict:
        """Convert notification to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'type': self.type,
            'category': self.category,
            'priority': self.priority,
            'title': self.title,
            'message': self.message,
            'action_text': self.action_text,
            'action_url': self.action_url,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat(),
            'time': self._get_relative_time(),
            'date': self.created_at.strftime('%b %d, %I:%M %p'),
            'notification_metadata': self.notification_metadata,
            'unread': not self.is_read
        }

    def _get_relative_time(self) -> str:
        """Get human-readable relative time"""
        now = datetime.now(timezone.utc)
        diff = now - self.created_at

        seconds = diff.total_seconds()
        minutes = seconds / 60
        hours = minutes / 60
        days = diff.days
        weeks = days / 7

        if seconds < 60:
            return 'Just now'
        elif minutes < 60:
            return f'{int(minutes)} min ago' if minutes > 1 else '1 min ago'
        elif hours < 24:
            return f'{int(hours)} hours ago' if hours > 1 else '1 hour ago'
        elif days < 7:
            return f'{days} days ago' if days > 1 else '1 day ago'
        elif weeks < 4:
            return f'{int(weeks)} weeks ago' if weeks > 1 else '1 week ago'
        else:
            return self.created_at.strftime('%b %d, %Y')


class NotificationPreference(db.Model):
    """User notification preferences"""
    __tablename__ = 'notification_preferences'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True, index=True)

    # Category Preferences
    trade_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    wallet_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    security_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    kyc_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    system_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    promotion_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    account_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Delivery Preferences
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    push_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    sms_notifications: Mapped[bool] = mapped_column(Boolean, default=False)

    # Email Digest Settings
    daily_digest: Mapped[bool] = mapped_column(Boolean, default=False)
    weekly_digest: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship
    user: Mapped["User"] = relationship(back_populates="notification_preferences")

    def __repr__(self) -> str:
        return f'<NotificationPreference for User {self.user_id}>'

    def to_dict(self) -> dict:
        """Convert preferences to dictionary"""
        return {
            'user_id': self.user_id,
            'categories': {
                'trade': self.trade_enabled,
                'wallet': self.wallet_enabled,
                'security': self.security_enabled,
                'kyc': self.kyc_enabled,
                'system': self.system_enabled,
                'promotion': self.promotion_enabled,
                'account': self.account_enabled,
            },
            'delivery': {
                'email': self.email_notifications,
                'push': self.push_notifications,
                'sms': self.sms_notifications,
            },
            'digest': {
                'daily': self.daily_digest,
                'weekly': self.weekly_digest,
            }
        }


# Usage Examples:
"""
# Creating notifications (in your route handlers or services):

from sqlalchemy.orm import Session

# 1. Trade notification
Notification.create_trade_notification(
    session=db.session,
    user_id=current_user.id,
    trade_data={
        'action': 'buy',
        'symbol': 'AAPL',
        'quantity': 10,
        'price': 185.40,
        'trade_id': 123
    }
)

# 2. Wallet notification
Notification.create_wallet_notification(
    session=db.session,
    user_id=current_user.id,
    wallet_data={
        'amount': 50000,
        'method': 'bank transfer',
        'transaction_id': 456
    },
    notification_type='deposit'
)

# 3. Security notification
Notification.create_security_notification(
    session=db.session,
    user_id=current_user.id,
    security_data={
        'title': 'New Login Detected',
        'message': 'A new login was detected from Lagos, Nigeria.',
        'ip_address': '192.168.1.1',
        'location': 'Lagos, Nigeria',
        'device': 'Chrome on Windows'
    }
)

# 4. KYC notification
Notification.create_kyc_notification(
    session=db.session,
    user_id=current_user.id,
    kyc_status='pending'
)

# Query notifications for a user (SQLAlchemy 2.0 style):
from sqlalchemy import select

# Get unread notifications
stmt = select(Notification).where(
    Notification.user_id == user_id,
    Notification.is_read == False,
    Notification.deleted_at == None
).order_by(Notification.created_at.desc())

notifications = db.session.execute(stmt).scalars().all()

# Get notifications by category
stmt = select(Notification).where(
    Notification.user_id == user_id,
    Notification.category == NotificationCategory.TRADE.value
).order_by(Notification.created_at.desc()).limit(10)

trade_notifications = db.session.execute(stmt).scalars().all()

# Mark as read
notification.mark_as_read(db.session)

# Mark all as read
from sqlalchemy import update

stmt = update(Notification).where(
    Notification.user_id == user_id,
    Notification.is_read == False
).values(
    is_read=True,
    read_at=datetime.utcnow()
)
db.session.execute(stmt)
db.session.commit()
"""