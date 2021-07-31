import requests
import time
from bs4 import BeautifulSoup
from mailjet_rest import Client
import os
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(message)s")

URL = "https://www.val-de-marne.gouv.fr/booking/create/4963/1"
HEADERS = {
    "connection": "keep-alive",
    "pragma": "no-cache",
    "cache-control": "no-cache",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en",
}
WAIT = 60 * 10
NOTIFICATION_URL = "https://hooknotifier.com/1625060231742/patient-cherry?business=Prefecture&object=RDV&body=La página ha cambiado"


def send_notification():
    response = requests.request("POST", NOTIFICATION_URL)
    if response.status_code != 200:
        logging.info("FAILED TO SEND NOTIFICATION", response.content)


def send_email():
    api_key = os.getenv("MAILJET_API_KEY")
    api_secret = os.getenv("MAILJET_API_SECRET")
    mailjet = Client(auth=(api_key, api_secret), version="v3.1")
    data = {
        "Messages": [
            {
                "From": {"Email": "pablo@jplm.me", "Name": "Pablo"},
                "To": [
                    {"Email": "pleasedontbelong@gmail.com", "Name": "Pablo"},
                    {"Email": "dayamitv@gmail.com", "Name": "Dayami"},
                ],
                "Subject": "Prefectura Nacionalizacion",
                "TextPart": f"La pagina de la nacionalizacion ha cambiado {URL}",
                "HTMLPart": f'La pagina de la nacionalizacion ha cambiado <a href="{URL}">{URL}</a>',
                "CustomID": "AppGettingStartedTest",
            }
        ]
    }
    result = mailjet.send.create(data=data)
    logging.info(result.status_code)
    logging.info(result.json())


def get_options():
    logging.info(f"Calling {URL}")
    response = requests.get(URL, headers=HEADERS)
    if not response.status_code == 200:
        logging.info(f"Error calling {URL}:", response.status_code)
        return
    logging.info("Response OK")
    soup = BeautifulSoup(response.content, "html.parser")
    options = sorted([o.get("value") for o in soup.select("input.radio")])
    return options


def run():
    options_count = False
    while True:
        try:
            current_count = get_options()
            if options_count is None:
                pass
            elif not options_count:
                options_count = current_count
            elif current_count:
                if current_count != options_count:
                    logging.info("HAS CHANGED!")
                    send_notification()
                    send_email()
                else:
                    logging.info("Still the same")
            time.sleep(WAIT)
        except Exception as e:
            logging.error("Something went wrong {e}")


if __name__ == "__main__":
    run()
