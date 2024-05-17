from pprint import pprint
from office.views import UserViewSet
from rich import print
from rich import pretty
import re
import hashlib


def show_users():
    view = UserViewSet()
    pprint(view.list())


def email_validation(email: str) -> bool:
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(pattern, email):
        return True
    return False


def username_exist(username: str, view: UserViewSet) -> bool:
    all_users = list(map(lambda item: item["username"], view.list()["objects"]))
    for temp_username in all_users:
        if temp_username == username:
            return True
    return False


def password_validation(username: str, password: str, view: UserViewSet) -> bool:
    correct_password = list(filter(lambda item: item["username"] == username, view.list()["objects"]))[0].get("password")
    encrypted_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    if correct_password == encrypted_password:
        return True
    return False


def check_activation(username: str, view: UserViewSet) -> bool:
    return list(filter(lambda item: item["username"] == username, view.list()["objects"]))[0].get("is_active")


def sign_up():
    view = UserViewSet()
    user_info = dict()
    username = input("Enter your username : ")
    while username_exist(username, view):
        username = input("There is a user with that username.\nPlease enter another username : ")
    user_info["username"] = username
    email = input("Enter your Email address :")
    while not email_validation(email):
        email = input("Invalid Email address!\nPlease try again : ")
    user_info["email"] = email
    user_info["password"] = input("Enter your password : ")
    print(user_info)
    print(view.create(user_info))


def log_in():
    view = UserViewSet()
    username = input("Enter your username : ")
    while not username_exist(username, view):
        username = input("There is a no user with that username.\nPlease try again : ")
    password = input("Enter your password :")
    while not password_validation(username, password, view):
        password = input("Invalid password !\nPlease try again : ")
    if not check_activation(username, view):
        print("Your account is not active.")
    else:
        print(f"{username} logged in successfully.")


def show_menu():
    options = {
        "Show users": show_users,
        "Sign Up": sign_up,
        "Log in": log_in
    }
    options_list = list(options.keys())
    for index in range(len(options_list)):
        print(f"{index + 1}. {options_list[index]}")
    user_input = int(input("Enter your Option: ")) - 1
    func = options[options_list[user_input]]
    func()


def main():
    show_menu()


if __name__ == "__main__":
    pretty.install()
    main()
