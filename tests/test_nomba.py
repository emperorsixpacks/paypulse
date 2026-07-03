import pytest
from unittest.mock import AsyncMock, patch, ANY
from src.paypulse.core.settings import NombaConfig
from src.paypulse.infrastructure.nomba import Nomba
from src.paypulse.infrastructure.nomba.dtos import (
    BankAccountTransferRequest,
    WalletTransferRequest,
    CreateVirtualAccountRequest,
)

@pytest.fixture
def nomba_client():
    config = NombaConfig(
        NOMBA_BASE_URL="https://sandbox.nomba.com",
        NOMBA_CLIENT_ID="test_client_id",
        NOMBA_CLIENT_SECRET="test_client_secret",
        NOMBA_ACCOUNT_ID="test_account_id",
    )
    client = Nomba(config)
    client._access_token = "mocked_token"
    client._refresh_token = "mocked_refresh"
    client._business_id = "mocked_biz"
    return client

@pytest.mark.asyncio
async def test_parent_account_details(nomba_client):
    with patch.object(nomba_client, "_get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = ({"success": True}, None)
        await nomba_client.parent_account_details()
        mock_get.assert_called_once_with(
            ANY,
            path_suffix="/v1/accounts/parent"
        )

@pytest.mark.asyncio
async def test_sub_account_details(nomba_client):
    with patch.object(nomba_client, "_get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = ({"success": True}, None)
        await nomba_client.sub_account_details(sub_account_id="sub_123")
        mock_get.assert_called_once_with(
            ANY,
            path_suffix="/v1/accounts/sub-account-details",
            req_params={"accountId": "sub_123"}
        )

@pytest.mark.asyncio
async def test_bank_transfer(nomba_client):
    with patch.object(nomba_client, "_post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = ({"success": True}, None)
        req = BankAccountTransferRequest(
            amount=1000.0,
            accountNumber="1234567890",
            accountName="Test Account",
            bankCode="044",
            merchantTxRef="ref_01"
        )
        await nomba_client.bank_transfer(req, sub_account_id="sub_123")
        mock_post.assert_called_once_with(
            ANY,
            path_suffix="/v2/transfers/bank/sub_123",
            data=req.model_dump()
        )

@pytest.mark.asyncio
async def test_bank_account_lookup(nomba_client):
    with patch.object(nomba_client, "_post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = ({"success": True}, None)
        await nomba_client.bank_account_lookup(account_number="1234567890", bank_code="044")
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["path_suffix"] == "/v1/transfers/bank/lookup"
        assert kwargs["data"] == {"accountNumber": "1234567890", "bankCode": "044"}

@pytest.mark.asyncio
async def test_requery_transaction(nomba_client):
    with patch.object(nomba_client, "_get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = ({"success": True}, None)
        await nomba_client.requery_transaction("session_abc")
        mock_get.assert_called_once_with(
            ANY,
            path_suffix="/v1/transactions/requery/session_abc"
        )


@pytest.mark.asyncio
async def test_tokenized_card_payment(nomba_client):
    from src.paypulse.infrastructure.nomba.dtos import TokenizedCardPaymentRequest
    with patch.object(nomba_client, "_post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = ({"success": True}, None)
        req = TokenizedCardPaymentRequest(tokenKey="tok_123")
        await nomba_client.tokenized_card_payment(req)
        mock_post.assert_called_once_with(
            ANY,
            path_suffix="/v1/checkout/tokenized-card-payment",
            data=req.model_dump(exclude_none=True)
        )


@pytest.mark.asyncio
async def test_list_tokenized_cards(nomba_client):
    with patch.object(nomba_client, "_get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = ({"success": True}, None)
        await nomba_client.list_tokenized_cards(customer_email="test@user.com")
        mock_get.assert_called_once_with(
            ANY,
            path_suffix="/v1/checkout/tokenized-card-data",
            req_params={"customerEmail": "test@user.com"}
        )


@pytest.mark.asyncio
async def test_update_tokenized_card_data(nomba_client):
    from src.paypulse.infrastructure.nomba.dtos import UpdateTokenizedCardDataRequest
    with patch.object(nomba_client, "_post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = ({"success": True}, None)
        req = UpdateTokenizedCardDataRequest(
            tokenKey="tok_123",
            currentEmailAddress="old@email.com",
            newEmailAddress="new@email.com"
        )
        await nomba_client.update_tokenized_card_data(req)
        mock_post.assert_called_once_with(
            ANY,
            path_suffix="/v1/checkout/tokenized-card-data",
            data=req.model_dump()
        )

