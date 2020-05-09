import time
import logging
from src.Twilio import Twilio
from flask import Flask, redirect, request

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s - %(module)s - %(funcName)s - %(lineno)d - %(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            f"logs/debug_{int(time.time())}.log",
            "w"
        ),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
twilio = Twilio()


@app.route('/', methods=['GET', 'POST'])
def authorize_callback():

    logging.info("Recieved a request!")
    body = {
        key: request.values.get(key)
        for key in request.values.keys()
    }
    logging.debug(f"Request contents = {body}")

    logging.debug("Generating reply...")
    reply = twilio.parseRequest(body)
    logging.info(f"Reply Generated = {reply}")

    # twilio.client.messages.create(reply)

    return ("", 200)


@app.route("/callback")
def handle_callback():

    logging.info("Callback recieved")
    logging.debug(request.get_json())

    return (200,)


if __name__ == "__main__":
    app.run(debug=True)
