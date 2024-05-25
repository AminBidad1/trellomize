from pprint import pprint
from rich import print, pretty
import re
import hashlib
from rich.console import Console
from office.views import UserViewSet, ProjectViewSet, TaskViewSet, CommentViewSet
from office.models import ProjectModel, Date, TaskModel, CommentModel


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


def add_task():
    user_view = UserViewSet()
    project_view = ProjectViewSet()
    username = console.input("Enter your username: ")
    if users := user_view.filter(username=username):
        user_id = users[0].get("id")
        project_title = console.input("Enter the project title: ")
        project_id = project_view.filter(title=project_title, leader_id=user_id)[0]["id"]
        title = console.input("Enter your title: ")
        description = console.input("Enter your description: ")
        started_at = Date.from_string(console.input("Enter start date and time: "))
        ended_at = Date.from_string(console.input("Enter end date and time: "))
        for i in range(1, 5):
            console.print(f"{i} - {TaskModel.Priority(i).name}")
        priority = int(console.input("Choice: "))
        for i in range(1, 6):
            console.print(f"{i} - {TaskModel.Status(i).name}")
        status = int(console.input("Choice: "))
        task = TaskModel(title=title, project_id=project_id, description=description,
                         started_at=started_at, ended_at=ended_at,
                         priority=priority, status=status)
        task.save()

        members_count = int(console.input("Enter your count of members: "))
        for index in range(1, members_count + 1):
            member_username = console.input(f"{index} - Enter the username of member: ")
            if m_users := user_view.filter(username=member_username):
                member_id = m_users[0].get("id")
                task.add_member(member_id=member_id)
            else:
                console.print("this username does not exist")
    else:
        print("the input is not valid.")


def show_tasks():
    view = TaskViewSet()
    print(view.list())


def add_comment():
    user_view = UserViewSet()
    task_view = TaskViewSet()
    username = console.input("Enter your username: ")
    if users := user_view.filter(username=username):
        user_id = users[0].get("id")
        task_title = console.input("Enter the task title: ")
        if tasks := task_view.filter(title=task_title):
            task_id = tasks[0].get("id")
            text = console.input("Enter your text: ")
            comment = CommentModel(task_id=task_id, text=text, user_id=user_id)
            comment.save()
        else:
            console.print("task does not exist")
    else:
        print("the input is not valid.")


def show_comments():
    view = CommentViewSet()
    view.list()


def show_menu():
    options = {
        "Show users": show_users,
        "Sign Up": sign_up,
        "Log in": log_in,
        "Show projects": show_projects,
        "Add project": add_project,
        "Show tasks": show_tasks,
        "Add task": add_task,
        "Show comments": show_comments,
        "Add comment": add_comment,
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
