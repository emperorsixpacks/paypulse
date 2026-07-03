from typing import Any

from httpx import Response

from src.paypulse.core.settings import NombaConfig
from src.paypulse.infrastructure.base_client import BaseClient, T
from src.paypulse.infrastructure.nomba.base import NombaResponse
from src.paypulse.infrastructure.nomba.dtos import (
    AccountBalanceResponse,
    AccountDetailsResponse,
    AuthTokenResponse,
    BankAccountLookupRequest,
    BankAccountLookupResponse,
    BankAccountTransferRequest,
    BankAccountTransferResponse,
    BanksListResponse,
    CancelCheckoutOrderResponse,
    CancelOrderRequest,
    CreateCheckoutOrderRequest,
    CreateCheckoutOrderResponse,
    CreateVirtualAccountRequest,
    CreateVirtualAccountResponse,
    DeleteTokenizedCardDataRequest,
    DeleteTokenizedCardDataResponse,
    FetchCheckoutTransactionResponse,
    FetchTransactionsResponse,
    FetchVirtualAccountResponse,
    FilterVirtualAccountRequest,
    FilterVirtualAccountsResponse,
    IssueTokenRequest,
    RefundCheckoutTransactionRequest,
    RefundCheckoutTransactionResponse,
    TokenizedCardListResponse,
    TokenizedCardPaymentRequest,
    TokenizedCardPaymentResponse,
    TransactionRequeryResponse,
    UpdateTokenizedCardDataRequest,
    UpdateTokenizedCardDataResponse,
    WalletTransferRequest,
    WalletTransferResponse,
)
from src.paypulse.types import Error, error


class NombaClient(BaseClient):
    def __init__(self, config: NombaConfig, path: str = "") -> None:
        self.config = config
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._business_id: str | None = None
        super().__init__(path)

    def _get_base_url(self) -> str:
        return self.config.nomba_base_url

    def _get_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "accountId": self.config.nomba_account_id,
        }
        if self._access_token:
            headers["Authorization"] = self._access_token
        return headers

    def _process_response(
        self, res: Response, response_model: type[T]
    ) -> tuple[T | None, Error]:
        if res.status_code >= 500:
            return None, error(f"Service not available {res.status_code}")

        response_data = response_model.model_validate(res.json())

        if isinstance(response_data, NombaResponse) and response_data.code not in (
            "00",
            "200",
            "201",
        ):
            return None, error(
                f"{response_data.description} code: {response_data.code}"
            )

        return response_data, None

    async def _ensure_authenticated(self) -> None:
        if self._access_token:
            return
        await self.authenticate()

    async def authenticate(self) -> tuple[AuthTokenResponse | None, Error]:
        request = IssueTokenRequest(
            client_id=self.config.nomba_client_id,
            client_secret=self.config.nomba_client_secret,
        )
        url = f"{self._get_base_url()}/v1/auth/token/issue"
        headers = {"accountId": self.config.nomba_account_id}
        from httpx import AsyncClient

        async with AsyncClient() as client:
            res = await client.post(
                url,
                json=request.model_dump(),
                headers=headers,
                timeout=30,
            )
            if not res.is_success:
                return None, error(f"Auth failed {res.status_code}: {res.text}")

            data = AuthTokenResponse.model_validate(res.json())
            if data.code not in ("00", "200"):
                return None, error(data.description)

            self._access_token = data.data.access_token
            self._refresh_token = data.data.refresh_token
            self._business_id = data.data.businessId
            return data, None

    async def refresh_token(self) -> tuple[AuthTokenResponse | None, Error]:
        if not self._refresh_token:
            return await self.authenticate()

        request = IssueTokenRequest(
            grant_type="refresh_token",
            client_id=self.config.nomba_client_id,
            client_secret=self.config.nomba_client_secret,
        )
        url = f"{self._get_base_url()}/v1/auth/token/issue"
        headers = {
            "accountId": self.config.nomba_account_id,
            "Authorization": self._access_token or "",
        }
        from httpx import AsyncClient

        async with AsyncClient() as client:
            res = await client.post(
                url,
                json=request.model_dump(),
                headers=headers,
                timeout=30,
            )
            if not res.is_success:
                self._access_token = None
                self._refresh_token = None
                return await self.authenticate()

            data = AuthTokenResponse.model_validate(res.json())
            self._access_token = data.data.access_token
            self._refresh_token = data.data.refresh_token
            self._business_id = data.data.businessId
            return data, None

    async def revoke_token(self) -> tuple[None, Error]:
        await self._ensure_authenticated()
        url = f"{self._get_base_url()}/v1/auth/token/revoke"
        from httpx import AsyncClient

        async with AsyncClient() as client:
            await client.post(
                url,
                headers=self._get_headers(),
                timeout=30,
            )
            self._access_token = None
            self._refresh_token = None
            return None, None


class AccountMixin:
    async def parent_account_balance(
        self: Any,
    ) -> tuple[AccountBalanceResponse | None, Error]:
        await self._ensure_authenticated()
        return await self._get(
            AccountBalanceResponse, path_suffix="/v1/accounts/balance"
        )

    async def parent_account_details(
        self: Any,
    ) -> tuple[AccountDetailsResponse | None, Error]:
        await self._ensure_authenticated()
        return await self._get(
            AccountDetailsResponse, path_suffix="/v1/accounts/parent"
        )

    async def sub_account_balance(
        self: Any, sub_account_id: str
    ) -> tuple[AccountBalanceResponse | None, Error]:
        await self._ensure_authenticated()
        return await self._get(
            AccountBalanceResponse,
            path_suffix=f"/v1/accounts/{sub_account_id}/balance",
        )

    async def sub_account_details(
        self: Any, sub_account_id: str | None = None, account_ref: str | None = None
    ) -> tuple[AccountDetailsResponse | None, Error]:
        await self._ensure_authenticated()
        params = {}
        if sub_account_id:
            params["accountId"] = sub_account_id
        if account_ref:
            params["accountRef"] = account_ref
        return await self._get(
            AccountDetailsResponse,
            path_suffix="/v1/accounts/sub-account-details",
            req_params=params or None,
        )


class TransferMixin:
    async def bank_transfer(
        self: Any, request: BankAccountTransferRequest, sub_account_id: str | None = None
    ) -> tuple[BankAccountTransferResponse | None, Error]:
        await self._ensure_authenticated()
        path = f"/v2/transfers/bank/{sub_account_id}" if sub_account_id else "/v2/transfers/bank"
        return await self._post(
            BankAccountTransferResponse,
            path_suffix=path,
            data=request.model_dump(),
        )

    async def wallet_transfer(
        self: Any, request: WalletTransferRequest, sub_account_id: str | None = None
    ) -> tuple[WalletTransferResponse | None, Error]:
        await self._ensure_authenticated()
        path = f"/v2/transfers/wallet/{sub_account_id}" if sub_account_id else "/v2/transfers/wallet"
        return await self._post(
            WalletTransferResponse,
            path_suffix=path,
            data=request.model_dump(),
        )

    async def bank_account_lookup(
        self: Any, account_number: str, bank_code: str
    ) -> tuple[BankAccountLookupResponse | None, Error]:
        await self._ensure_authenticated()
        request = BankAccountLookupRequest(
            accountNumber=account_number,
            bankCode=bank_code,
        )
        return await self._post(
            BankAccountLookupResponse,
            path_suffix="/v1/transfers/bank/lookup",
            data=request.model_dump(),
        )

    async def fetch_bank_codes(self: Any) -> tuple[BanksListResponse | None, Error]:
        await self._ensure_authenticated()
        return await self._get(BanksListResponse, path_suffix="/v1/transfers/banks")


class VirtualAccountMixin:
    async def create_virtual_account(
        self: Any, request: CreateVirtualAccountRequest, sub_account_id: str | None = None
    ) -> tuple[CreateVirtualAccountResponse | None, Error]:
        await self._ensure_authenticated()
        path = f"/v1/accounts/virtual/{sub_account_id}" if sub_account_id else "/v1/accounts/virtual"
        return await self._post(
            CreateVirtualAccountResponse,
            path_suffix=path,
            data=request.model_dump(),
        )

    async def fetch_virtual_account(
        self: Any, account_id: str
    ) -> tuple[FetchVirtualAccountResponse | None, Error]:
        await self._ensure_authenticated()
        return await self._get(
            FetchVirtualAccountResponse,
            path_suffix=f"/v1/accounts/virtual/{account_id}",
        )

    async def filter_virtual_accounts(
        self: Any,
        request: FilterVirtualAccountRequest | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> tuple[FilterVirtualAccountsResponse | None, Error]:
        await self._ensure_authenticated()
        req_params = {}
        if limit is not None:
            req_params["limit"] = limit
        elif "limit" in kwargs:
            req_params["limit"] = kwargs.pop("limit")
        if cursor is not None:
            req_params["cursor"] = cursor
        elif "cursor" in kwargs:
            req_params["cursor"] = kwargs.pop("cursor")

        if request is None and kwargs:
            request = FilterVirtualAccountRequest(**kwargs)

        body = request.model_dump(exclude_none=True) if request else {}
        return await self._post(
            FilterVirtualAccountsResponse,
            path_suffix="/v1/accounts/virtual/list",
            data=body if body else None,
            req_params=req_params if req_params else None,
        )


class CheckoutMixin:
    async def create_checkout_order(
        self: Any, request: CreateCheckoutOrderRequest
    ) -> tuple[CreateCheckoutOrderResponse | None, Error]:
        await self._ensure_authenticated()
        return await self._post(
            CreateCheckoutOrderResponse,
            path_suffix="/v1/checkout/order",
            data=request.model_dump(),
        )

    async def fetch_checkout_transaction(
        self: Any, order_reference: str
    ) -> tuple[FetchCheckoutTransactionResponse | None, Error]:
        await self._ensure_authenticated()
        return await self._get(
            FetchCheckoutTransactionResponse,
            path_suffix=f"/v1/checkout/order/{order_reference}",
        )

    async def cancel_checkout_order(
        self: Any, order_reference: str
    ) -> tuple[CancelCheckoutOrderResponse | None, Error]:
        await self._ensure_authenticated()
        request = CancelOrderRequest(orderReference=order_reference)
        return await self._post(
            CancelCheckoutOrderResponse,
            path_suffix="/v1/checkout/order/cancel",
            data=request.model_dump(),
        )

    async def refund_checkout_transaction(
        self: Any, order_reference: str, request: RefundCheckoutTransactionRequest
    ) -> tuple[RefundCheckoutTransactionResponse | None, Error]:
        await self._ensure_authenticated()
        return await self._post(
            RefundCheckoutTransactionResponse,
            path_suffix=f"/v1/checkout/order/{order_reference}/refund",
            data=request.model_dump(exclude_none=True),
        )

    async def tokenized_card_payment(
        self: Any, request: TokenizedCardPaymentRequest
    ) -> tuple[TokenizedCardPaymentResponse | None, Error]:
        await self._ensure_authenticated()
        return await self._post(
            TokenizedCardPaymentResponse,
            path_suffix="/v1/checkout/tokenized-card-payment",
            data=request.model_dump(exclude_none=True),
        )

    async def list_tokenized_cards(
        self: Any,
        customer_email: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page: int | None = None,
    ) -> tuple[TokenizedCardListResponse | None, Error]:
        await self._ensure_authenticated()
        params = {}
        if customer_email is not None:
            params["customerEmail"] = customer_email
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date
        if page is not None:
            params["page"] = page
        return await self._get(
            TokenizedCardListResponse,
            path_suffix="/v1/checkout/tokenized-card-data",
            req_params=params or None,
        )

    async def update_tokenized_card_data(
        self: Any, request: UpdateTokenizedCardDataRequest
    ) -> tuple[UpdateTokenizedCardDataResponse | None, Error]:
        await self._ensure_authenticated()
        return await self._post(
            UpdateTokenizedCardDataResponse,
            path_suffix="/v1/checkout/tokenized-card-data",
            data=request.model_dump(),
        )

    async def delete_tokenized_card_data(
        self: Any, request: DeleteTokenizedCardDataRequest
    ) -> tuple[DeleteTokenizedCardDataResponse | None, Error]:
        await self._ensure_authenticated()
        from src.paypulse.types import HTTPMethod
        # Delete helper doesn't exist in base class, so we can use _send
        url = self._get_url("/v1/checkout/tokenized-card-data")
        res, err = await self._send(url, HTTPMethod.DELETE, data=request.model_dump())
        if err:
            return None, err
        return self._process_response(res, DeleteTokenizedCardDataResponse)



class TransactionMixin:
    async def fetch_transactions(
        self: Any, sub_account_id: str | None = None, **params: Any
    ) -> tuple[FetchTransactionsResponse | None, Error]:
        await self._ensure_authenticated()
        path = f"/v1/transactions/accounts/{sub_account_id}" if sub_account_id else "/v1/transactions/accounts"
        return await self._get(
            FetchTransactionsResponse,
            path_suffix=path,
            req_params=params or None,
        )

    async def fetch_transaction(
        self: Any, transaction_id: str, sub_account_id: str | None = None
    ) -> tuple[TransactionRequeryResponse | None, Error]:
        await self._ensure_authenticated()
        path = (
            f"/v1/transactions/accounts/{sub_account_id}/single"
            if sub_account_id
            else "/v1/transactions/accounts/single"
        )
        return await self._get(
            TransactionRequeryResponse,
            path_suffix=path,
            req_params={"transactionRef": transaction_id},
        )

    async def requery_transaction(
        self: Any, session_id: str
    ) -> tuple[TransactionRequeryResponse | None, Error]:
        await self._ensure_authenticated()
        return await self._get(
            TransactionRequeryResponse,
            path_suffix=f"/v1/transactions/requery/{session_id}",
        )


class AccountManager(NombaClient, AccountMixin):
    def __init__(self, config: NombaConfig) -> None:
        super().__init__(config)


class TransferManager(NombaClient, TransferMixin):
    def __init__(self, config: NombaConfig) -> None:
        super().__init__(config)


class VirtualAccountManager(NombaClient, VirtualAccountMixin):
    def __init__(self, config: NombaConfig) -> None:
        super().__init__(config)


class CheckoutManager(NombaClient, CheckoutMixin):
    def __init__(self, config: NombaConfig) -> None:
        super().__init__(config)


class TransactionManager(NombaClient, TransactionMixin):
    def __init__(self, config: NombaConfig) -> None:
        super().__init__(config)


class Nomba(
    NombaClient,
    AccountMixin,
    TransferMixin,
    VirtualAccountMixin,
    CheckoutMixin,
    TransactionMixin,
):
    def __init__(self, config: NombaConfig) -> None:
        super().__init__(config)
