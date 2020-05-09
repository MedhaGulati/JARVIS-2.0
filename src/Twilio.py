import os
import re
import sys
import time
import spacy
import random
import atexit
import pickle
import logging
import requests
import configparser

from src.User import User
from src.constants import *
from src.Vision import Vision
from twilio.rest import Client
from src.KG import google_search
from src.Language import Language
from src.UploadIM import UploadIM
from allennlp.predictors.predictor import Predictor


class Twilio:

    def __init__(self):

        try:
            logging.debug("Loading config...")
            self.config = configparser.ConfigParser()
            self.config.read('config.ini')
            logging.info("Config loaded!")
        except Exception as e:
            self.config = None
            logging.exception(e)

        try:
            logging.debug("Loading Client...")
            self.client = Client(
                self.config['AUTH']['ACCOUNT_SID'],
                self.config['AUTH']['AUTH_TOKEN']
            )
            logging.info("Client loaded!")
        except Exception as e:
            self.client = None
            logging.exception(e)

        logging.debug("Initializing Language...")
        self.lang = Language()
        logging.info("Language loaded.")

        self.USER_DUMP_FILE = self.config["USER"]["DUMP"]
        self.USER_REGISTER_STRING = """
            Please send your ERP credentials in format - Username/Password
        """

        try:
            logging.debug("Loading users from file...")
            self.users = self.loadUsers()
            temp = [
                (user.fetchAttendance(), user.fetchTimeTable())
                for user in self.users
            ]
            logging.info(f"Users loaded - {len(self.users)}")
        except Exception as e:
            logging.exception(e)
            logging.error("Error loading users.")
            self.users = []

        self.body = None
        self.reply_cache = None
        self.cred_check_matcher = re.compile("^\\d{2}[a-zA-Z]{3}\\d{3}\/.+")
        self.reply = {
            "to": None,
            "from_": None,
            "body": None
        }

        self.imgur = UploadIM()
        self.vision = Vision()

        atexit.register(self.saveUsers, self.users)

        # try:
        #     logging.debug("Initializing predictor...")
        #     self.predictor = Predictor.from_path(
        #         self.config["ML"]["PREDICTOR"]
        #     )
        #     logging.info("Predictor Initialized!")
        # except Exception as e:
        #     self.predictor = None
        #     logging.exception(e)

        # try:
        #     logging.debug("Loading dataset from file...")
        #     with open(self.config["ML"]["DATASET"]) as dataset:
        #         self.dataset = dataset.read()
        #     logging.info("Dataset Loaded!")
        # except Exception as e:
        #     self.dataset = ""
        #     logging.exception(e)

    def searchUser(self, number):

        logging.debug(f"Searching for user with {number}...")
        for user in self.users:
            logging.debug(user.username + ": " + user.number)
            if user.number == number:
                logging.info("User found!")
                return user

        logging.error("User not found.")
        return None

    def registerUser(self):

        logging.debug("Initialting register process...")

        # Check cache
        if self.reply_cache:
            if self.reply_cache['body'] == self.USER_REGISTER_STRING:
                # Check body for username/pass
                logging.debug("Verifying creds...")
                is_valid = self.cred_check_matcher.match(self.body['Body'])
                if is_valid:
                    logging.info("Creds verified.")
                    username = is_valid.string.split("/")[0]
                    password = is_valid.string.split("/")[-1]
                    self.users.append(
                        User(
                            username=username,
                            password=password,
                            number=self.body['From']
                        )
                    )
                    self.reply['body'] = "Successfully registered!"
                    self.saveUsers(self.users)

                else:
                    self.reply['body'] = "Error Registering"
            else:
                self.reply['body'] = self.USER_REGISTER_STRING
        else:
            self.reply['body'] = self.USER_REGISTER_STRING

    def is_between(self, time, time_range):
        if time_range[1] < time_range[0]:
            return time >= time_range[0] or time <= time_range[1]
        return time_range[0] <= time <= time_range[1]

    def handleUserQuery(self, user):

        logging.debug("Handling user input...")

        self.query = self.lang.parse(self.body["Body"])
        attr = self.query.keys()

        logging.debug(f"Query - {self.query}")
        logging.debug("\n" + str(user.attendance))
        logging.debug("\n" + str(user.timeTable))

        if ENTITY in attr:
            if re.search("(attd)|(attn)|(att)", self.query[ENTITY].lower()):
                self.queryAttendance(user)
            elif re.search("(class)|(cls)", self.query[ENTITY].lower()):
                self.queryTimeTable(user)
            else:
                if QUERY in attr:
                    if re.search("(google)", self.query[QUERY].lower()):
                        search_res = google_search(self.query[ENTITY])
                        self.reply['body'] = "\n> ".join(search_res)
                        return
                self.reply['body'] = random.choice(NOT_FOUND)
                logging.error("Not found")

        else:
            self.reply['body'] = random.choice(NOT_FOUND)
            logging.error("Not found")

    def queryAttendance(self, user):
        logging.debug("Querieing attendance...")
        res = None

        if COURSE in self.query.keys():
            res = user.attendance[
                user.attendance["Course_Name"].str.lower().str.contains(
                    self.query[COURSE].lower())
            ]
            logging.debug("\n" + str(res))
        else:
            self.reply['body'] = random.choice(NOT_FOUND)
            logging.error("Course not found")

        if QUERY in self.query.keys():
            if re.search("(view)", self.query[QUERY].lower()):
                res_format = {
                    "subject": res["Course_Name"].iloc[0],
                    "totalLects": res["Total_Lectures"].iloc[0],
                    "present": res["Total_Present"].iloc[0],
                    "abs": res["Total_Absent"].iloc[0],
                    "loa": res["Leave_Of_Absence"].iloc[0],
                    "attendance": res["Attendance"].iloc[0]
                }

                self.reply['body'] = VIEW_ALL.format(**res_format)
                return

            if re.search("(refresh)", self.query[QUERY].lower()):
                user.fetchTimeTable(refresh=True)
                user.fetchAttendance(refresh=True)
                self.reply['body'] = random.choice(DONE)
                return

        if len(res) < 1:
            self.reply['body'] = random.choice(NOT_FOUND)
            logging.error("Not found")
            return

        self.reply['body'] = random.choice(
            ATTENDANCE
        ).format(res["Attendance"].iloc[0])

    def queryTimeTable(self, user):
        logging.debug("Querieing Time Table...")

        now = time.strftime("%I:%M %p")
        today = time.strftime("%A").lower()

        now = "10:00 AM"
        today = "friday"

        if QUERY in self.query.keys():
            if re.search("(what)", self.query[QUERY].lower()):
                if TIME in self.query.keys():
                    if re.search("(current)", self.query[TIME].lower()):
                        for i in range(len(user.timeTable)):
                            df = user.timeTable.iloc[i]
                            if today == df["Day"].lower():
                                if self.is_between(now, (df["Start_Time"], df["End_Time"])):
                                    res_format = {
                                        "course": df["Course"],
                                        "finish": df["End_Time"]
                                    }
                                    self.reply['body'] = CURRENT_CLASS.format(
                                        **res_format)
                                    return

            if re.search("(when)", self.query[QUERY].lower()):
                if TIME in self.query.keys():
                    if re.search("(next)", self.query[TIME].lower()):
                        for i in range(len(user.timeTable)):
                            df = user.timeTable.iloc[i]
                            if today == df["Day"].lower():
                                if df["Start_Time"] > now:
                                    res_format = {
                                        "course": df["Course"],
                                        "start": df["Start_Time"]
                                    }
                                    self.reply['body'] = NEXT_CLASS.format(
                                        **res_format)
                                    return

            # if re.search("(which)", self.query[QUERY].lower()):
            #     if TIME in self.query.keys():
            #         if re.search("(next)", self.query[TIME].lower()):
            #             for i in range(len(user.timeTable)):
            #                 df = user.timeTable.iloc[i]
            #                 if today == df["Day"].lower():
            #                     if df["Start_Time"] > now:
            #                         res_format = {
            #                             "course": df["Course"],
            #                             "start": df["Start_Time"]
            #                         }
            #                         self.reply['body'] = NEXT_CLASS.format(
            #                             **res_format)
            #                         return

        self.reply['body'] = random.choice(NOT_FOUND)

    def handleImageQuery(self):

        logging.debug("Handling image query...")

        output_img = self.image.split(
            ".")[0] + "_out." + self.image.split(".")[-1]
        detection = self.vision.detectImage(self.image, output_img)
        logging.debug(detection)
        self.reply['media_url'] = self.imgur.getLink(output_img)
        logging.debug(self.reply['media_url'])

        return

    def parseRequest(self, body):

        logging.debug("Parsing request...")

        self.reply = {
            "to": None,
            "from_": None,
            "body": None,
            "media_url": None
        }

        self.body = body
        self.reply['to'] = self.body['From']
        self.reply['from_'] = self.body['To']

        if int(self.body["NumMedia"]) > 0:
            if "image" in self.body["MediaContentType0"]:
                self.image = "images/" + \
                    str(int(time.time())) + "." + \
                    self.body["MediaContentType0"].split("/")[-1]
            r = requests.get(self.body["MediaUrl0"], verify=False)
            with open(self.image, 'wb') as outfile:
                outfile.write(r.content)
            self.handleImageQuery()
            return self.sendMessage(self.reply)

        user = self.searchUser(body["From"])
        if user:
            self.handleUserQuery(user)
        else:
            self.registerUser()

        return self.sendMessage(self.reply)

    def sendMessage(self, reply):
        self.reply_cache = reply
        self.client.messages.create(**reply)
        return reply

    def saveUsers(self, users, file="data/user_dump.dat"):
        with open(file, "wb") as dump:
            pickle.dump(users, dump)

        logging.debug("Users saved.")

    def loadUsers(self, file="data/user_dump.dat"):
        with open(file, "rb") as dump:
            return pickle.load(dump)
