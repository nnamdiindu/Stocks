from datetime import datetime
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

    # Action Fields (for actionable notifications)
    action_text: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    action_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Status Tracking
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Metadata & Context
    # metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
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

    # Composite Indexes for performance
    __table_args__ = (
        Index('idx_user_read_created', 'user_id', 'is_read', 'created_at'),
        Index('idx_user_category', 'user_id', 'category'),
        Index('idx_expires_deleted', 'expires_at', 'deleted_at'),
    )

    def __repr__(self) -> str:
        return f'<Notification {self.id}: {self.title} for User {self.user_id}>'

    def mark_as_read(self, session) -> None:
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
            session.commit()

    def mark_as_unread(self, session) -> None:
        """Mark notification as unread"""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            session.commit()

    def soft_delete(self, session) -> None:
        """Soft delete notification (user dismissed it)"""
        self.deleted_at = datetime.utcnow()
        session.commit()

    def is_expired(self) -> bool:
        """Check if notification has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

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
            'metadata': self.metadata,
            'unread': not self.is_read  # For template compatibility
        }

    def _get_relative_time(self) -> str:
        """Get human-readable relative time"""
        now = datetime.utcnow()
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

    @staticmethod
    def create_trade_notification(session, user_id: int, trade_data: dict) -> "Notification":
        """Helper method to create trade-related notifications"""
        notification = Notification(
            user_id=user_id,
            type=NotificationType.SUCCESS.value,
            category=NotificationCategory.TRADE.value,
            priority=NotificationPriority.NORMAL.value,
            title='Trade Successful',
            message=f"Your order to {trade_data['action']} {trade_data['symbol']} has been completed at ${trade_data['price']} per share.",
            metadata={
                'symbol': trade_data['symbol'],
                'quantity': trade_data['quantity'],
                'price': trade_data['price'],
                'action': trade_data['action']
            },
            related_object_type='Trade',
            related_object_id=trade_data.get('trade_id')
        )
        session.add(notification)
        session.commit()
        return notification

    @staticmethod
    def create_wallet_notification(session, user_id: int, wallet_data: dict,
                                   notification_type: str = 'deposit') -> "Notification":
        """Helper method to create wallet-related notifications"""
        if notification_type == 'deposit':
            title = 'Wallet Funded'
            message = f"${wallet_data['amount']:,.2f} has been successfully added to your wallet via {wallet_data['method']}."
            notif_type = NotificationType.SUCCESS.value
        elif notification_type == 'withdrawal':
            title = 'Withdrawal in Progress'
            message = f"Your withdrawal request of ${wallet_data['amount']:,.2f} is being processed."
            notif_type = NotificationType.INFO.value
        else:
            title = 'Wallet Activity'
            message = wallet_data.get('message', 'Your wallet has been updated.')
            notif_type = NotificationType.INFO.value

        notification = Notification(
            user_id=user_id,
            type=notif_type,
            category=NotificationCategory.WALLET.value,
            priority=NotificationPriority.NORMAL.value,
            title=title,
            message=message,
            metadata=wallet_data,
            related_object_type='Transaction',
            related_object_id=wallet_data.get('transaction_id')
        )
        session.add(notification)
        session.commit()
        return notification

    @staticmethod
    def create_security_notification(session, user_id: int, security_data: dict) -> "Notification":
        """Helper method to create security-related notifications"""
        notification = Notification(
            user_id=user_id,
            type=NotificationType.DANGER.value,
            category=NotificationCategory.SECURITY.value,
            priority=NotificationPriority.URGENT.value,
            title=security_data.get('title', 'Security Alert'),
            message=security_data['message'],
            metadata={
                'ip_address': security_data.get('ip_address'),
                'location': security_data.get('location'),
                'device': security_data.get('device'),
                'timestamp': datetime.utcnow().isoformat()
            },
            action_text='Secure Account',
            action_url='/settings?tab=security'
        )
        session.add(notification)
        session.commit()
        return notification

    @staticmethod
    def create_kyc_notification(session, user_id: int, kyc_status: str = 'pending') -> "Notification":
        """Helper method to create KYC-related notifications"""
        messages = {
            'pending': 'Please complete your KYC / identity verification to enable withdrawals and unlock all features.',
            'approved': 'Your KYC verification has been approved! You now have full access to all features.',
            'rejected': 'Your KYC verification was not approved. Please review the requirements and try again.'
        }

        types = {
            'pending': NotificationType.WARNING.value,
            'approved': NotificationType.SUCCESS.value,
            'rejected': NotificationType.DANGER.value
        }

        notification = Notification(
            user_id=user_id,
            type=types.get(kyc_status, NotificationType.INFO.value),
            category=NotificationCategory.KYC.value,
            priority=NotificationPriority.HIGH.value,
            title='KYC Verification' if kyc_status == 'pending' else f'KYC {kyc_status.capitalize()}',
            message=messages.get(kyc_status, messages['pending']),
            action_text='Verify now' if kyc_status == 'pending' else None,
            action_url='/settings?tab=kyc' if kyc_status == 'pending' else None
        )
        session.add(notification)
        session.commit()
        return notification


class NotificationPreference(db.Model):
    """
    User notification preferences - controls what notifications users receive
    """
    __tablename__ = 'notification_preferences'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True, index=True)

    # Category Preferences (enable/disable by category)
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

    def should_send_notification(self, category: str) -> bool:
        """Check if user wants to receive notifications for this category"""
        category_map = {
            NotificationCategory.TRADE.value: self.trade_enabled,
            NotificationCategory.WALLET.value: self.wallet_enabled,
            NotificationCategory.SECURITY.value: self.security_enabled,
            NotificationCategory.KYC.value: self.kyc_enabled,
            NotificationCategory.SYSTEM.value: self.system_enabled,
            NotificationCategory.PROMOTION.value: self.promotion_enabled,
            NotificationCategory.ACCOUNT.value: self.account_enabled,
        }
        return category_map.get(category, True)

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