import sys
import pickle
import random
from src.User import User

# sys.path.append(1, "C:\\Users\\Aaditya Verma\\Documents\\Python\\JARVIS")


def generateRandomUsers(num=10):
    letters = [chr(x) for x in range(65, 91)]
    symbols = [chr(x) for x in range(32, 128)]
    numbers = [str(x) for x in range(9)]

    return [
        User(
            "".join([random.choice(letters) for _ in range(5)]),
            "".join([random.choice(symbols) for _ in range(10)]),
            "".join([random.choice(numbers) for _ in range(10)]),
        ) for i in range(num)
    ]


def displayUsers(userlist):
    for user in userlist:
        print(f"{user.username} with number {user.number}")


def saveUsers(userlist, file="data/user_dump.dat"):
    with open(file, "wb") as dump:
        pickle.dump(userlist, dump)


def loadUsers(file="data/user_dump.dat"):
    with open(file, "rb") as dump:
        return pickle.load(dump)


def main():
    print("Generating users...")
    users = generateRandomUsers(10)
    print("Users generated...")
    displayUsers(users)
    print("Saving users...")
    saveUsers(users)
    print("Users saved...")
    users_loaded = loadUsers()
    print("Users loaded...")
    displayUsers(users_loaded)


if __name__ == "__main__":
    main()
