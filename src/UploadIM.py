import configparser
from imgurpython import ImgurClient


class UploadIM:

    def __init__(self):

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.id = self.config["AUTH"]["IMGUR_ID"]
        self.secret = self.config["AUTH"]["IMGUR_SECRET"]

        self.client = ImgurClient(self.id, self.secret)

    def getLink(self, image_path):

        image = self.client.upload_from_path(image_path)

        return image['link']
