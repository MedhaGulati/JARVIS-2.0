import time
import logging
from src.Twilio import Twilio

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


def main():

    twilio = Twilio()

    # print(twilio.parseRequest(
    #     {
    #         "To": "3485342",
    #         "From": "56543",
    #         "Body": "Hello"
    #     }
    # ))

    # print(twilio.parseRequest(
    #     {
    #         "To": "3485342",
    #         "From": "56543",
    #         "Body": "16CSU001/16CSU001"
    #     }
    # ))

    print(twilio.parseRequest(
        {
            "To": "3485342",
            "From": "56543",
            "Body": "Screenshot of attendance",
            "NumMedia": "0"
        }
    ))


if __name__ == "__main__":
    main()
