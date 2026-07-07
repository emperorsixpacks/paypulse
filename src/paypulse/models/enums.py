from enum import Enum


class BillingInterval(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class SubscriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"
    TRIALING = "TRIALING"
    EXPIRED = "EXPIRED"


class InvoiceStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    VOID = "VOID"


class BillingAttemptStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"


class WebhookDeliveryStatus(str, Enum):
    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class CheckoutStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class BillingType(str, Enum):
    FIXED = "FIXED"
    METERED = "METERED"


class RefundStatus(str, Enum):
    NONE = "NONE"
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
