import requests


def tell_telegram(msg, config):
    if not config.telegram_user: return
    send_text = f'https://api.telegram.org/bot{config.telegram_token}/sendMessage?chat_id={config.telegram_user}&parse_mode=Markdown&text={msg}'
    response = requests.get(send_text)
    return response.json()

def tell_telegram_when_done(func):
    def wrapper(*args, **kwargs):
        results = func(*args, **kwargs)
        telegram_bot_send(f"{func.__name__} with args {args} and kwargs {kwargs} has finished.")
        return results
    return wrapper

def telegram_bot_get_updates(config):
    if not config.telegram_token:
        return
    send_text = f'https://api.telegram.org/bot{config.telegram_token}/getUpdates'
    response = requests.get(send_text)
    return response.json()