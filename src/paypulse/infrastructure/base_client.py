import json
from abc import ABC, abstractmethod
from typing import Any

from httpx import AsyncClient, ConnectError, Response, TimeoutException
from pydantic import BaseModel

from src.paypulse.types import Error, HTTPMethod, error, httpError

type T = BaseModel


class BaseClient(ABC):
    def __init__(self, path: str) -> None:
        self._path = path

    @abstractmethod
    def _get_base_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _get_headers(self) -> dict[str, str]:
        raise NotImplementedError

    def _get_url(self, path_suffix: str = "") -> str:
        return f"{self._get_base_url()}{self._path}{path_suffix}"

    async def _send(
        self,
        url: str,
        method: str,
        *,
        data: dict[str, Any] | None = None,
        req_params: dict[str, Any] | None = None,
    ) -> tuple[Response | None, Error]:
        headers = self._get_headers()
        async with AsyncClient() as client:
            try:
                res = await client.request(
                    method,
                    url,
                    headers=headers,
                    json=data,
                    params=req_params,
                    timeout=30,
                )
                return res, None
            except (
                TimeoutException,
                ConnectError,
                json.JSONDecodeError,
                TypeError,
            ) as e:
                return None, httpError(code=504, message=f"Request to {url} failed: {e}")

    def _process_response(self, res: Response, response_model: type[T]) -> tuple[T | None, Error]:
        if res.status_code >= 500:
            return None, httpError(
                code=res.status_code,
                message=f"Service not available {res.status_code}",
            )

        if not res.is_success:
            return None, httpError(
                code=res.status_code,
                message=f"Request failed {res.status_code}: {res.text}",
            )

        response_data = response_model.model_validate(res.json())
        return response_data, None

    async def _get(
        self,
        response_model: type[T],
        path_suffix: str = "",
        req_params: dict[str, Any] | None = None,
    ) -> tuple[T | None, Error]:
        url = self._get_url(path_suffix)
        res, err = await self._send(url, HTTPMethod.GET, req_params=req_params)
        if err:
            return None, err
        return self._process_response(res, response_model)

    async def _post(
        self,
        response_model: type[T],
        path_suffix: str = "",
        data: dict[str, Any] | None = None,
        req_params: dict[str, Any] | None = None,
    ) -> tuple[T | None, Error]:
        url = self._get_url(path_suffix)
        res, err = await self._send(url, HTTPMethod.POST, data=data, req_params=req_params)
        if err:
            return None, err
        return self._process_response(res, response_model)

    async def _put(
        self,
        response_model: type[T],
        path_suffix: str = "",
        data: dict[str, Any] | None = None,
        req_params: dict[str, Any] | None = None,
    ) -> tuple[T | None, Error]:
        url = self._get_url(path_suffix)
        res, err = await self._send(url, HTTPMethod.PUT, data=data, req_params=req_params)
        if err:
            return None, err
        return self._process_response(res, response_model)
