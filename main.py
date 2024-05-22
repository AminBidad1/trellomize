from pprint import pprint
from rich import print, pretty
import re
import hashlib
from rich.console import Console
from libs.log import log
from office.views import UserViewSet, ProjectViewSet
from office.models import ProjectModel


def show_users():
    view = UserViewSet()
    pprint(view.list())


def email_validation(email: str, view: UserViewSet) -> bool:
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
    correct_password = list(filter(
        lambda item: item["username"] == username, view.list()["objects"]
    ))[0].get("password")
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
    if username == "return":
        return
    while username_exist(username, view):
        username = console.input("[bold red]There is a user with that username."
                                 "[/bold red]\n[bold yellow]please enter another username : [/bold yellow]")
        if username == "return":
            return
    user_info["username"] = username
    email = console.input("[bold cyan]Enter your Email address :[/bold cyan]")
    if email == "return":
        return
    while not email_validation(email, view):
        email = console.input("[bold yellow]Please try again : [/bold yellow]")
        if email == "return":
            return
    user_info["email"] = email
    user_info["password"] = console.input("[bold cyan]Enter your password : [/bold cyan]")
    # print(user_info)
    view.create(user_info)
    # show_menu("main",)


def log_in():
    view = UserViewSet()
    username = console.input("[bold cyan]Enter your username : [/bold cyan]")
    if username == "return":
        return
    while not username_exist(username, view):
        username = console.input("[bold red]There is a no user with that username.[/bold red]\n"
                                 "[bold yellow]Please try again : [/bold yellow]")
        if username == "return":
            return
    password = console.input("[bold cyan]Enter your password :[/bold cyan]")
    if password == "return":
        return
    while not password_validation(username, password, view):
        password = console.input("[bold red]Invalid password ![/bold red]\n"
                                 "[bold yellow]Please try again : [/bold yellow]")
        if password == "return":
            return
    if not check_activation(username, view):
        print("[bold red]Your account is not active.[/bold red]")
    else:
        print(f"[bold green]{username} logged in successfully.[/bold green]")
        # print(log.info("ailreza"))
        show_menu("logged", list(filter(lambda item: item["username"] == username, view.list()["objects"]))[0].get("id"))


def users_activity():
    view = UserViewSet()
    users = list(map(lambda item: item["username"], view.list()["objects"]))
    user_activity = dict()
    for user in users:
        user_activity[user] = list(filter(lambda item: item["username"] == user, view.list()["objects"]))[0].get("is_active")
    print(user_activity)
    user_input = console.input("Enter username to change activity: ")

    
def show_projects():
    view = ProjectViewSet()
    pprint(view.list())


def add_project():
    view = UserViewSet()
    username = console.input("Enter your username: ")
    if users := view.filter(username=username):
        user_id = users[0].get("id")
        title = console.input("Enter your title: ")
        project = ProjectModel(title=title, leader_id=user_id)
        project.save()
        members_count = int(console.input("Enter your count of members: "))
        for index in range(1, members_count + 1):
            member_username = console.input(f"{index} - Enter the username of member: ")
            if m_users := view.filter(username=member_username):
                member_id = m_users[0].get("id")
                project.add_member(member_id=member_id)
            else:
                console.print("this username does not exist")
    else:
        print("the input is not valid.")


def show_menu(type: str, user_id: int):
    view = UserViewSet()
    options = {
        "Show users": show_users,
        "Sign Up": sign_up,
        "Log in": log_in,
        "Change users activity": users_activity,
        "Show projects": show_projects,
        "Add project": add_project,
    }
    options_list = list(options.keys())
    if type == "main":
        options_list.pop(0)
        options_list.pop(2)
    elif not list(filter(lambda item: item["id"] == user_id, view.list()["objects"]))[0].get("is_admin"):
        for i in range(4):
            options_list.pop(0)
    else:
        for i in range(3):
            options_list.pop(0)

    for index in range(len(options_list)):
        print(f"{index + 1}. {options_list[index]}")
    user_input = int(input("Enter your Option: ")) - 1
    if user_input == -1:
        return
    func = options[options_list[user_input]]
    func()
    show_menu(type, user_id)


def main():
    show_menu("main", 0)


if __name__ == "__main__":
    pretty.install()
    console = Console()
    main()
