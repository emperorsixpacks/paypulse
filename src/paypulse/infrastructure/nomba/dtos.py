from datetime import datetime
from typing import Any

from pydantic import Field

from src.paypulse.infrastructure.nomba.base import BaseNombaType, CheckoutCurrency, NombaResponse, PaymentMethod


class IssueTokenRequest(BaseNombaType):
    grant_type: str = "client_credentials"
    client_id: str
    client_secret: str


class IssueTokenResponse(BaseNombaType):
    businessId: str
    access_token: str
    refresh_token: str
    expiresAt: str


class AuthTokenResponse(NombaResponse):
    data: IssueTokenResponse


class AccountBalanceData(BaseNombaType):
    amount: str
    currency: str
    timeCreated: datetime


class AccountBalanceResponse(NombaResponse):
    data: AccountBalanceData


class AccountDetailsData(BaseNombaType):
    accountId: str
    accountName: str
    accountNumber: str | None = None
    bankName: str | None = None
    bvn: str | None = None
    currency: str | None = None
    timeCreated: datetime | None = None
    createdAt: datetime | None = None
    accountHolderId: str | None = None
    accountRef: str | None = None
    status: str | None = None
    type: str | None = None
    banks: list[Any] | None = None


class AccountDetailsResponse(NombaResponse):
    data: AccountDetailsData


class BankAccountTransferRequest(BaseNombaType):
    amount: float
    accountNumber: str = Field(min_length=10, max_length=10)
    accountName: str
    bankCode: str
    merchantTxRef: str
    senderName: str | None = None
    narration: str | None = None


class BankAccountTransferMeta(BaseNombaType):
    api_rrn: str | None = None
    narration: str | None = None
    recipientName: str | None = None
    sender_name: str | None = None
    merchantTxRef: str | None = None
    api_client_id: str | None = None
    currency: str | None = None
    accountNumber: str | None = None
    bankName: str | None = None
    bankCode: str | None = None
    sessionId: str | None = None
    amount_charged: str | None = None
    paymentVendor: str | None = None
    wallet_balance: str | None = None
    wallet_currency: str | None = None
    paymentVendorReference: str | None = None


class BankAccountTransferResult(BaseNombaType):
    amount: str | float
    source: str | None = None
    sourceUserId: str | None = None
    productId: str | None = None
    meta: BankAccountTransferMeta | None = None
    fee: float | None = None
    timeCreated: datetime | None = None
    id: str | None = None
    type: str | None = None
    status: str | None = None


class BankAccountTransferResponse(NombaResponse):
    data: BankAccountTransferResult | None = None
    status: bool | None = None
    message: str | None = None


class WalletTransferRequest(BaseNombaType):
    amount: float
    recipientAccountId: str
    narration: str | None = None
    merchantTxRef: str


class WalletTransferMetaObject(BaseNombaType):
    merchantTxRef: str | None = None
    api_client_id: str | None = None
    api_account_id: str | None = None
    rrn: str | None = None


class WalletTransferResult(BaseNombaType):
    amount: float | str
    meta: WalletTransferMetaObject | None = None
    fee: float | None = None
    timeCreated: datetime | None = None
    id: str | None = None
    type: str | None = None
    status: str | None = None


class WalletTransferResponse(NombaResponse):
    data: WalletTransferResult | None = None


class Bank(BaseNombaType):
    code: str
    name: str


class BanksListData(BaseNombaType):
    results: list[Bank]


class BanksListResponse(NombaResponse):
    data: BanksListData


class BankAccountLookupRequest(BaseNombaType):
    accountNumber: str
    bankCode: str


class BankAccountLookupData(BaseNombaType):
    accountNumber: str
    accountName: str
    bankCode: str | None = None


class BankAccountLookupResponse(NombaResponse):
    data: BankAccountLookupData


class CreateVirtualAccountRequest(BaseNombaType):
    accountRef: str = Field(min_length=16, max_length=64)
    accountName: str = Field(min_length=8, max_length=64)
    bvn: str | None = None
    expiryDate: str | None = None
    expectedAmount: float | None = None


class VirtualAccountBank(BaseNombaType):
    bankName: str | None = None
    bankAccountNumber: str | None = None
    bankAccountName: str | None = None


class CreateVirtualAccountData(BaseNombaType):
    createdAt: datetime
    accountHolderId: str | None = None
    accountRef: str
    bvn: str | None = None
    accountName: str
    bankName: str | None = None
    bankAccountNumber: str | None = None
    bankAccountName: str | None = None
    currency: str | None = None
    callbackUrl: str | None = None
    expired: bool | None = None
    banks: list[VirtualAccountBank] | None = None


class CreateVirtualAccountResponse(NombaResponse):
    data: CreateVirtualAccountData


class VirtualAccountData(BaseNombaType):
    accountId: str | None = None
    accountRef: str
    accountName: str
    bvn: str | None = None
    currency: str | None = None
    bankName: str | None = None
    bankAccountNumber: str | None = None
    bankAccountName: str | None = None
    expired: bool | None = None
    createdAt: datetime | None = None
    banks: list[VirtualAccountBank] | None = None


class FetchVirtualAccountResponse(NombaResponse):
    data: VirtualAccountData | None = None


class FilterVirtualAccountRequest(BaseNombaType):
    accountName: str | None = None
    accountRef: str | None = None
    bvn: str | None = None
    bankAccountNumber: str | None = None
    dateCreatedFrom: str | None = None
    dateCreatedTo: str | None = None
    expired: bool | None = None
    resourceAcquired: bool | None = None


class FilterVirtualAccountsResponse(NombaResponse):
    data: list[VirtualAccountData] | None = None


class Order(BaseNombaType):
    orderReference: str | None = None
    customerId: str | None = None
    callbackUrl: str
    customerEmail: str
    amount: float
    currency: CheckoutCurrency
    accountId: str | None = None
    allowedPaymentMethods: list[PaymentMethod] | None = None
    splitRequest: dict[str, Any] | None = None
    orderMetaData: dict[str, str] | None = None


class CreateCheckoutOrderRequest(BaseNombaType):
    order: Order
    tokenizeCard: bool | None = None


class CreateCheckoutOrderData(BaseNombaType):
    checkoutLink: str
    orderReference: str


class CreateCheckoutOrderResponse(NombaResponse):
    data: CreateCheckoutOrderData


class CheckoutTransactionData(BaseNombaType):
    id: str | None = None
    orderReference: str | None = None
    status: str | None = None
    amount: float | None = None
    currency: str | None = None
    customerEmail: str | None = None
    paymentMethod: str | None = None
    timeCreated: datetime | None = None


class FetchCheckoutTransactionResponse(NombaResponse):
    data: CheckoutTransactionData | None = None


class CancelOrderRequest(BaseNombaType):
    orderReference: str


class CancelCheckoutOrderData(BaseNombaType):
    success: bool
    message: str


class CancelCheckoutOrderResponse(NombaResponse):
    data: CancelCheckoutOrderData | None = None


class RefundCheckoutTransactionRequest(BaseNombaType):
    amount: float | None = None
    reason: str | None = None


class RefundCheckoutTransactionResponse(NombaResponse):
    data: dict[str, Any] | None = None


class TransactionData(BaseNombaType):
    id: str | None = None
    amount: str | float | None = None
    type: str | None = None
    status: str | None = None
    accountName: str | None = None
    accountNumber: str | None = None
    bankCode: str | None = None
    bankName: str | None = None
    narration: str | None = None
    merchantTxRef: str | None = None
    fee: float | None = None
    timeCreated: datetime | None = None
    sessionId: str | None = None
    currency: str | None = None


class FetchTransactionsResponse(NombaResponse):
    data: list[TransactionData] | None = None


class TransactionRequeryResponse(NombaResponse):
    data: TransactionData | None = None


class TokenizedCardPaymentRequest(BaseNombaType):
    order: Order | None = None
    tokenKey: str


class TokenizedCardPaymentResult(BaseNombaType):
    status: bool | str | None = None
    message: str | None = None


class TokenizedCardPaymentResponse(NombaResponse):
    data: TokenizedCardPaymentResult


class TokenizedCardData(BaseNombaType):
    tokenKey: str
    customerEmail: str
    cardType: str | None = None
    cardPan: str | None = None
    tokenExpirationDate: str | None = None


class TokenizedCardListResult(BaseNombaType):
    nextPage: str | int | None = None
    tokenizedCardDataList: list[TokenizedCardData] | None = None


class TokenizedCardListResponse(NombaResponse):
    data: TokenizedCardListResult | None = None


class UpdateTokenizedCardDataRequest(BaseNombaType):
    tokenKey: str
    currentEmailAddress: str
    newEmailAddress: str


class UpdateTokenizedCardDataResult(BaseNombaType):
    status: bool | str | None = None
    message: str | None = None
    tokenizedCardData: list[TokenizedCardData] | None = None


class UpdateTokenizedCardDataResponse(NombaResponse):
    data: UpdateTokenizedCardDataResult


class DeleteTokenizedCardDataRequest(BaseNombaType):
    tokenKey: str


class DeleteTokenizedCardDataResult(BaseNombaType):
    status: bool | str | None = None
    message: str | None = None


class DeleteTokenizedCardDataResponse(NombaResponse):
    data: DeleteTokenizedCardDataResult

