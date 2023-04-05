import requests

from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def tell_telegram(msg, config):
    if not config.telegram_user:
        return
    send_text = f"https://api.telegram.org/bot{config.telegram_token}/sendMessage?chat_id={config.telegram_user}&parse_mode=Markdown&text={msg}"

    with requests.Session() as session:
        retries = Retry(
            total=10, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504]
        )

        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.mount("https://", HTTPAdapter(max_retries=retries))

        response = session.get(send_text)
        return response.json()


def telegram_bot_get_updates(config):
    if not config.telegram_token:
        return
    send_text = f"https://api.telegram.org/bot{config.telegram_token}/getUpdates"
    response = requests.get(send_text)
    return response.json()