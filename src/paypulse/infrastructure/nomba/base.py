from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class BaseNombaType(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="allow",
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )


class NombaResponse(BaseNombaType):
    code: str
    description: str


class TransactionStatus(StrEnum):
    SUCCESS = "SUCCESS"
    PENDING_BILLING = "PENDING_BILLING"
    FAILED = "FAILED"
    REFUND = "REFUND"


class TransactionType(StrEnum):
    WITHDRAWAL = "withdrawal"
    PURCHASE = "purchase"
    TRANSFER = "transfer"
    P2P = "p2p"
    ONLINE_CHECKOUT = "online_checkout"
    QRT_CREDIT = "qrt_credit"
    QRT_DEBIT = "qrt_debit"


class CheckoutCurrency(StrEnum):
    NGN = "NGN"
    CDF = "CDF"
    USD = "USD"


class PaymentMethod(StrEnum):
    CARD = "Card"
    TRANSFER = "Transfer"
    NOMBA_QR = "Nomba QR"
    USSD = "USSD"
    BUY_NOW_PAY_LATER = "Buy Now Pay Later"
    MOMO = "MOMO"
    INTL_CARD = "Intl Card"
    APPLE_PAY = "Apple Pay"
