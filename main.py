from pprint import pprint
from rich import print, pretty
import re
import hashlib
from rich.console import Console
from libs.log import log
from office.views import UserViewSet, ProjectViewSet, UserProjectViewSet
from office.models import ProjectModel


def show_users(user_id: str):
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


def sign_up(user_id: str):
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


def log_in(user_id: str):
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


def users_activity(user_id: str):
    view = UserViewSet()
    users = list(map(lambda item: item["username"], view.list()["objects"]))
    user_activity = dict()
    for user in users:
        user_activity[user] = list(filter(lambda item: item["username"] == user, view.list()["objects"]))[0].get("is_active")
    print(user_activity)
    user_input = console.input("Enter username to change activity: ")


def project_environment(project_id: str):
    pview = ProjectViewSet()
    upview = UserProjectViewSet()
    view = UserViewSet()
    console.print("Title : ", list(filter(lambda item: item["id"] == project_id, pview.list()["objects"]))[0].get("title"))
    leader_id = list(filter(lambda item: item["id"] == project_id, pview.list()["objects"]))[0].get("leader_id")
    console.print("Leader : ", list(filter(lambda item: item["id"] == leader_id, view.list()["objects"]))[0].get("username"))
    users = list(filter(lambda item: item["project_id"] == project_id, upview.list()["objects"]))
    console.print("Users : ")
    for user in users:
        if user.get("user_id") != leader_id:
            console.print(list(filter(lambda item: item["id"] == user.get("user_id"), view.list()["objects"]))[0].get("username"))


def add_task():
    pass


def show_tasks():
    pass


def manage_task():
    pass


def delete_user():
    pass


def delete_project():
    pass


def show_project_options(user_id: str, project_id: str):
    options = {
        "Add task": add_task,
        "Show tasks": show_tasks,
        "Manage task": manage_task,
        "Delete users": delete_user,
        "Delete project": delete_project,
    }
    options_list = list(options.keys())
    for index in range(len(options_list)):
        print(f"{index + 1}. {options_list[index]}")
    user_input = int(input("Enter your Option: ")) - 1
    if user_input == -1:
        return
    func = options[options_list[user_input]]
    # func(user_id)
    # show_project_options(type, user_id)


def show_projects(user_id: str):
    view = UserProjectViewSet()
    pview = ProjectViewSet()
    user_projects_id = list()
    console.print("You are leader of these projects :")
    for project in list(filter(lambda item: item["leader_id"] == user_id, pview.list()["objects"])):
        user_projects_id.append(project.get("id"))
        console.print(f"{len(user_projects_id)}. {project.get("title")}")
    print("\nYou are normal user in these projects :")
    projects = list(filter(lambda item: item["user_id"] == user_id, view.list()["objects"]))
    for project in projects:
        is_ok = True
        for lproject in list(filter(lambda item: item["leader_id"] == user_id, pview.list()["objects"])):
            if project.get("project_id") == lproject.get("id"):
                is_ok = False
        if is_ok:
            user_projects_id.append(project.get("project_id"))
            console.print(f"{len(user_projects_id)}. {list(filter(lambda item: item["id"] == project.get("project_id"), pview.list()["objects"]))[0].get("title")}")
    user_number = int(console.input("Enter number of project to open:"))
    if user_number == 0:
        return
    project_environment(user_projects_id[user_number-1])
    show_project_options(user_id, user_projects_id[user_number-1])


def can_add(project_id: str, user_id: str, count: int) -> bool:
    view = UserViewSet()
    pview = UserProjectViewSet()
    if username_exist(list(filter(lambda item: item["id"] == user_id, view.list()["objects"]))[0].get("username"), view):
        users_in_project = list(filter(lambda item: item["project_id"] == project_id, pview.list()["objects"]))
        for i in range(count):
            if users_in_project[i].get("user_id") == user_id:
                console.print()
                return False
        return True
    return False


def title_exist(title: str,) -> bool:
    pview = ProjectViewSet()
    if len(list(filter(lambda item: item["title"] == title, pview.list()["objects"]))) == 0:
        return True
    return False


def add_project(user_id: str):
    view = UserViewSet()
    title = console.input("[bold cyan]Enter your title: [/bold cyan]")
    if title == "return":
        return
    while not title_exist(title):
        if title == "return":
            return
        title = console.input("[bold red]There is a project with this title.[/bold red]\n"
                              "[bold yellow]Please try again : [/bold yellow]")
    project = ProjectModel(title=title, leader_id=user_id)
    project.save()
    project.add_member(member_id=user_id)
    members_count = int(console.input("Enter your count of members: "))
    index = 1
    while index < members_count + 1:
        member_username = console.input(f"{index} - Enter the username of member: ")
        if member_username == "return":
            return
        if not username_exist(member_username, view):
            console.print("There is no user with this username.")
            continue
        member_id = list(filter(lambda item: item["username"] == member_username, view.list()["objects"]))[0].get("id")
        if can_add(project.id, list(filter(lambda item: item["username"] == member_username, view.list()["objects"]))[0].get("id"), index):
            project.add_member(member_id=member_id)
            index = index + 1
        else:
            console.print("You cant add this user.")


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
def show_menu(type: str, user_id: str):
    view = UserViewSet()
    options = {
        "Show users": show_users,
        "Sign Up": sign_up,
        "Log in": log_in,
        "Change users activity": users_activity,
        "Show projects": show_projects,
        "Add project": add_project,
        "Show tasks": show_tasks,
        "Add task": add_task,
        "Show comments": show_comments,
        "Add comment": add_comment,
    }
    options_list = list(options.keys())
    if type == "main":
        options_list.pop(0)
        options_list.pop(2)
        options_list.pop(2)
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
    func(user_id)
    show_menu(type, user_id)


def main():
    show_menu("main", 0)


if __name__ == "__main__":
    pretty.install()
    console = Console()
    main()
