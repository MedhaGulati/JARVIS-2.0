import re
import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class User:

    def __init__(self, username, password, number, url="https://erp.ncuindia.edu/"):

        logging.debug("Creating user...")

        self.username = username
        self.password = password
        self.number = number
        self.url = url

        try:
            logging.debug("Loading time table.")
            self.timeTable = pd.read_csv(
                "data/" +
                self.username +
                "_TimeTable.csv"
            )
        except Exception as e:
            logging.error("No time table found.")
            self.timeTable = None

        try:
            logging.debug("Loading Attendance.")
            self.attendance = pd.read_csv(
                "data/" +
                self.username +
                "_Attendance.csv"
            )
        except Exception as e:
            logging.error("Attendance found.")
            self.attendance = None

    def getGreeting(self):
        return f"Welcome {self.username}!"

    def fetchTimeTable(self, refresh=False):

        logging.debug("Fetching Time Table...")

        if not refresh:
            try:
                logging.debug("Loading time table.")
                self.timeTable = pd.read_csv(
                    "data/" +
                    self.username +
                    "_TimeTable.csv"
                )
                return
            except Exception as e:
                logging.error("No time table found.")
                self.timeTable = None

        try:
            logging.debug("Loading driver...")
            driver = webdriver.Chrome()
            logging.info("Driver loaded.")

            driver.get(self.url)

            logging.debug("Finding elements...")
            user = driver.find_element_by_id("tbUserName")
            pswd = driver.find_element_by_id("tbPassword")

            logging.debug("Filling creds...")
            user.send_keys(self.username)
            pswd.send_keys(self.password)
            pswd.send_keys(Keys.RETURN)
            logging.info("Logged in.")

            logging.debug("Closing pop-ups...")
            pop_up = driver.find_element_by_id("popup_ok")
            pop_up.send_keys(Keys.RETURN)

            logging.debug("Fetching Time Table text...")
            tt = driver.find_element_by_id("divMytimetable")

            logging.info("Time Table fetched!")

            self.timeTable = self.parseRawTimeTable(tt)
            pd.to_csv("data/" + self.username + "_" +
                      "TimeTable.csv", index=False)

        except Exception as e:
            logging.exception(e)
            logging.error("Unable to fetch time table!")

        finally:
            driver.close()

    def parseRawTimeTable(self, tt):

        logging.debug("Parsing raw time table...")

        columns = ["Date", "Day", "Course",
                   "Faculty", "Start_Time", "End_Time"]

        date_pttrn = re.compile("(\\d+-\\w+-\\d+ \\w+)")
        time_table = date_pttrn.split(tt.text)[1:]

        sep = ":-"
        df = {k: [] for k in columns}

        for i in range(0, len(time_table) - 1, 2):
            sched = time_table[i+1].split("\n")
            for j in range(0, len(sched) - 1, 3):
                df["Date"].append(time_table[i].split(" ")[0])
                df["Day"].append(time_table[i].split(" ")[-1])
                df["Faculty"].append(sched[j].split(sep)[-1].strip())
                df["Course"].append(sched[j+1].split(sep)[-1].strip())
                df["Start_Time"].append(
                    sched[j+2].split(sep)[-1].split("To")[0].strip())
                df["End_Time"].append(
                    sched[j+2].split(sep)[-1].split("To")[-1].strip())

        logging.info("Time table parsed.")

        return pd.DataFrame(df)

    def fetchAttendance(self, refresh=False):

        logging.debug("Fetching attendance...")

        if not refresh:
            try:
                logging.debug("Loading Attendance.")
                self.attendance = pd.read_csv(
                    "data/" +
                    self.username +
                    "_Attendance.csv"
                )
                return
            except Exception as e:
                logging.error("Attendance found.")
                self.attendance = None

        try:
            logging.debug("Loading driver...")
            driver = webdriver.Chrome()
            logging.info("Driver loaded.")

            driver.get(self.url)

            logging.debug("Finding elements...")
            user = driver.find_element_by_id("tbUserName")
            pswd = driver.find_element_by_id("tbPassword")

            logging.debug("Filling creds...")
            user.send_keys(self.username)
            pswd.send_keys(self.password)
            pswd.send_keys(Keys.RETURN)
            logging.info("Logged in.")

            logging.debug("Closing pop-ups...")
            pop_up = driver.find_element_by_id("popup_ok")
            pop_up.send_keys(Keys.RETURN)

            logging.debug("Fetching Attendance text...")
            attendance = driver.find_element_by_id("aAttandance")
            attendance.click()
            attendance_table = driver.find_element_by_xpath(
                '//*[contains(concat( " ", @class, " " ), concat( " ", "altBgTdLast", " " ))]'
            )

            self.attendance = self.parseRawAttendace(attendance_table)
            self.attendance.to_csv("data/" + self.username + "_" +
                                   "Attendance.csv", index=False)
            logging.info("Attendace fetched!")

        except Exception as e:
            logging.exception(e)
            logging.error("Unable to fetch attendance!")

        finally:
            driver.close()

    def parseRawAttendace(self, attendance):

        logging.debug("Parsing attendance...")

        columns = ["Course_Code", "Course_Name", "Total_Lectures",
                   "Total_Present", "Total_Absent",
                   "Leave_Of_Absence", "Attendance"]
        df = {k: [] for k in columns}

        att = attendance.text.split("\n")[1:]
        for i in range(len(att)):
            df["Course_Code"].append(
                re.split("-", att[i])[0].split()[-1]
            )
            df["Course_Name"].append(
                " ".join(re.split("-", att[i])[-1].split()[:-6])
            )
            df["Total_Lectures"].append(
                re.split("-", att[i])[-1].split()[-6:-1][0]
            )
            df["Total_Present"].append(
                re.split("-", att[i])[-1].split()[-6:-1][1]
            )
            df["Total_Absent"].append(
                re.split("-", att[i])[-1].split()[-6:-1][2]
            )
            df["Leave_Of_Absence"].append(
                re.split("-", att[i])[-1].split()[-6:-1][3]
            )
            df["Attendance"].append(
                re.split("-", att[i])[-1].split()[-6:-1][4]
            )

        df = pd.DataFrame(df)
        for col in columns[2:]:
            df[col] = df[col].astype('float')

        return df
