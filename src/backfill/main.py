import concurrent.futures
import logging

from models.ohlcv_model import CryptoAPIResponse
from services.api_client import CryptoAPIClient
from services.s3_uploader import S3DataLakeUploader

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

NOME_DO_BUCKET = "lakehouse-crypto-bronze-gclauar"


def processar_moeda(simbolo: str):
    """Função que será executada para cada moeda."""
    client_api = CryptoAPIClient()
    uploader_s3 = S3DataLakeUploader(bucket_name=NOME_DO_BUCKET)

    data_inicio_ts = 1609459200000  # 01/01/2021 00:00:00
    data_fim_ts = 1778543999000  # 11/05/2026 23:59:59

    while data_inicio_ts < data_fim_ts:
        api_response = client_api.fetch_historical_data(
            symbol=simbolo,
            start_time=data_inicio_ts,
            end_time=data_fim_ts,
            interval="1h",
        )

        if not api_response:
            logging.info(f"Fim dos dados alcançado para a moeda {simbolo}")
            break

        list_cryptos = []
        for row in api_response:
            list_cryptos.append(
                {
                    "open_time": row[0],
                    "open": row[1],
                    "high": row[2],
                    "low": row[3],
                    "close": row[4],
                    "volume": row[5],
                    "quote_asset_volume": row[7],
                    "number_of_trades": row[8],
                    "taker_buy_base_asset_volume": row[9],
                }
            )

        crypto_valid = CryptoAPIResponse(data=list_cryptos)

        crypto_json_str = crypto_valid.model_dump_json()

        primeiro_candle = crypto_valid.data[0].open_time
        year = f"{primeiro_candle.year:04d}"
        month = f"{primeiro_candle.month:02d}"
        day = f"{primeiro_candle.day:02d}"

        s3_key = f"api_binance/moeda={simbolo}/ano={year}/mes={month}/dia={day}/lote_{data_inicio_ts}.json"

        uploader_s3.upload_json(json_data=crypto_json_str, s3_key=s3_key)

        data_inicio_ts = api_response[-1][0] + 1


def orquestrador_principal():

    moedas = [
        "BTCUSDT",  # Bitcoin
        "ETHUSDT",  # Ethereum
        "SOLUSDT",  # Solana
        "ADAUSDT",  # Cardano
        "AVAXUSDT",  # Avalanche
        "DOTUSDT",  # Polkadot
        "LINKUSDT",  # Chainlink
        "MATICUSDT",  # Polygon
        "ATOMUSDT",  # Cosmos
        "UNIUSDT",  # Uniswap
        "AAVEUSDT",  # Aave
        "MKRUSDT",  # Maker
        "DOGEUSDT",  # Dogecoin
        "SHIBUSDT",  # Shiba Inu
        "PEPEUSDT",  # Pepe
    ]

    logging.info(f"Iniciando Backfill Multithread para {len(moedas)} moedas...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(processar_moeda, moedas)

    logging.info("Pipeline de Backfill finalizado com sucesso!")


if __name__ == "__main__":
    orquestrador_principal()
