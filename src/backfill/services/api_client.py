import logging

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.backfill.core.exceptions import APIConnectionError, APIRateLimitError

logger = logging.getLogger(__name__)


class CryptoAPIClient:
    def __init__(self, base_url: str = "https://api.binance.com"):
        self.sessao = requests.Session()

        self.sessao.headers.update({"Accept": "application/json"})

        self.endpoint = f"{base_url}/api/v3/klines"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def fetch_historical_data(
        self, symbol: str, start_time: int, end_time: int, interval: str = "1h"
    ) -> list:
        """
        Busca 1 página de dados (1000 linhas) da Binance.
        Levanta exceções customizadas em caso de erro.
        """
        logger.info(f"Consultando API: {symbol} | startTime: {start_time}")

        params_binance = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": 1000,
        }

        response = self.sessao.get(self.endpoint, params=params_binance, timeout=10)

        if response.status_code == 429:
            logger.warning("Rate limit atingido! Tenacity entrará em ação...")
            raise APIRateLimitError(f"Erro 429 Rate limit: {response.text}")

        if response.status_code in [400, 401, 403, 404]:
            logger.error(f"Erro na requisição: {response.text}")
            raise APIConnectionError(f"Erro {response.status_code}: {response.text}")

        response.raise_for_status()

        return response.json()
