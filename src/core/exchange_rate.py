import requests
import logging
from bs4 import BeautifulSoup
from functools import lru_cache
import re

logger = logging.getLogger(__name__)


@lru_cache(maxsize=50)
def get_exchange_rate(from_currency, to_currency, amount):
    """
    Obtém a taxa de câmbio entre duas moedas e converte o valor informado.
    :param from_currency: Moeda de origem (default: BRL)
    :param to_currency: Moeda de destino (default: EUR)
    :param amount: Valor a ser convertido (default: 1)
    :return: Valor convertido ou None se ocorrer erro.
    """

    try:

        url = f"https://www.xe.com/currencyconverter/convert/?Amount={amount}&From={from_currency}&To={to_currency}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            logger.error(f"Erro ao acessar o site: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        result_element = soup.find("p", class_="sc-63d8b7e3-1 bMdPIi")
        if not result_element:
            logger.error("Não foi possível encontrar a taxa de câmbio na página.")
            return None

        result_text = result_element.text.strip()
        rate_match = re.search(r"[\d.]+", result_text)

        if rate_match:
            rate = float(rate_match.group())
            converted_amount = rate
            return converted_amount
        else:
            logger.error("Não foi possível extrair os números do texto.")
            return None

    except Exception as e:
        logger.error(f"Erro ao obter a taxa de câmbio: {e}")
        return None


if __name__ == "__main__":
    from_currency = "USD"
    to_currency = "BRL"
    amount = 0.30
    converted_value = get_exchange_rate(from_currency, to_currency, amount)

    if converted_value:
        print(
            f"{amount} {from_currency} equivale a {converted_value:.2f} {to_currency}"
        )
    else:
        print(
            f"Não foi possível obter a conversão de {from_currency} para {to_currency}."
        )
