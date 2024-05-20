from pprint import pprint
from office.views import UserViewSet
from rich import print, pretty
import re
import hashlib
from rich.console import Console


def show_users():
    view = UserViewSet()
    pprint(view.list())


def email_validation(email: str,view: UserViewSet) -> bool:
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(pattern, email):
        if email_exist(email, view):
            console.print("[bold red]there is a user with this Email address![/bold red]")
            return False
        else:
            return True
    console.print("[bold red]Invalid Email address![/bold red]")
    return False


def username_exist(username: str, view: UserViewSet) -> bool:
    all_users = list(map(lambda item: item["username"], view.list()["objects"]))
    for temp_username in all_users:
        if temp_username == username:
            return True
    return False


def email_exist(email: str, view: UserViewSet) -> bool:
    all_users = list(map(lambda item: item["email"], view.list()["objects"]))
    for temp_username in all_users:
        if temp_username == email:
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
    username = console.input("[bold cyan]Enter your username : [/bold cyan]")
    while username_exist(username, view):
        username = console.input("[bold red]There is a user with that username."
                                 "[/bold red]\n[bold yellow]please enter another username : [/bold yellow]")
    user_info["username"] = username
    email = console.input("[bold cyan]Enter your Email address :[/bold cyan]")
    while not email_validation(email, view):
        email = console.input("[bold yellow]Please try again : [/bold yellow]")
    user_info["email"] = email
    user_info["password"] = console.input("[bold cyan]Enter your password : [/bold cyan]")
    print(user_info)
    print(view.create(user_info))


def log_in():
    view = UserViewSet()
    username = console.input("[bold cyan]Enter your username : [/bold cyan]")
    while not username_exist(username, view):
        username = console.input("[bold red]There is a no user with that username.[/bold red]\n"
                                 "[bold yellow]Please try again : [/bold yellow]")
    password = console.input("[bold cyan]Enter your password :[/bold cyan]")
    while not password_validation(username, password, view):
        password = console.input("[bold red]Invalid password ![/bold red]\n"
                                 "[bold yellow]Please try again : [/bold yellow]")
    if not check_activation(username, view):
        print("[bold red]Your account is not active.[/bold red]")
    else:
        print(f"[bold green]{username} logged in successfully.[/bold green]")


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
    console = Console()
    main()
