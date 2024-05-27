from datetime import datetime
from rich import print, pretty
import re
import hashlib
from libs.log import log
from settings import ROOT_DIR
from office.views import (
    UserViewSet,
    ProjectViewSet,
    UserProjectViewSet,
    TaskViewSet,
    CommentViewSet
)
from rich.console import Console
from rich.table import Table
from office.models import ProjectModel, TaskModel, Date, CommentModel


# TODO: are you sure
def is_number(_input: str) -> bool:
    """
    check the input is number or not
    :param _input: str
    :return: bool
    """
    if _input == "":
        return False
    for i in _input:
        if i not in "0123456789":
            return False
    return True


def email_validation(email: str, view: UserViewSet) -> bool:
    """
    validate email based on regex
    :param email: str
    :param view: UserViewSet
    :return: bool
    """
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
    """
    check the username exists in database or not
    :param username: str
    :param view: UserViewSet
    :return: bool
    """
    all_users = list(map(lambda item: item["username"], view.list()))
    for temp_username in all_users:
        if temp_username == username:
            return True
    return False


def email_exist(email: str, view: UserViewSet) -> bool:
    """
    check the email exists in database or not
    :param email: str
    :param view: UserViewSet
    :return: bool
    """
    all_users = list(map(lambda item: item["email"], view.list()))
    for temp_username in all_users:
        if temp_username == email:
            return True
    return False


def password_validation(username: str, password: str, view: UserViewSet) -> bool:
    """
    check the password is correct or not
    :param username: str
    :param password: str
    :param view: UserViewSet
    :return: bool
    """
    correct_password = list(filter(
        lambda item: item["username"] == username, view.list()
    ))[0].get("password")
    encrypted_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    if correct_password == encrypted_password:
        return True
    return False


def check_activation(username: str) -> bool:
    """
    check the user is active or not
    :param username: str
    :return: bool
    """
    view = UserViewSet()
    return view.filter(username=username)[0].get("is_active")


def sign_up(user_id: str) -> None:
    """
    create a new user account
    :param user_id: str
    :return: None
    """
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
    password = console.input("[bold cyan]Enter your password : [/bold cyan]")
    if password == "return":
        return
    user_info["password"] = password
    view.create(user_info)
    console.print("[bold green]Account creation was successful[/bold green]")
    log.info(f"{username} signed up.")


def log_in(user_id: str) -> None:
    """
    log in
    :return: None
    """
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
    if not check_activation(username):
        console.print("[bold red]Your account is not active.[/bold red]")
    else:
        console.print(f"[bold green]{username} logged in successfully.[/bold green]")
        log.info(f"{username} logged in.")
        show_menu("logged", list(filter(lambda item: item["username"] == username, view.list()))[0].get("id"))


def users_activity(user_id: str) -> None:
    """
    change the activation of user
    :param user_id: str
    :return: None
    """
    while True:
        view = UserViewSet()
        users = view.list()
        table = Table()
        table.add_column("Username", justify="full", style="cyan")
        table.add_column("Activity", justify="full", style="chartreuse1")
        for user in users:
            if user.get("is_active"):
                table.add_row(user.get("username"), "Active")
            else:
                table.add_row(user.get("username"), "Blocked")
        print(table)
        user_input = console.input("[bright_green]Enter username to change activity: [/bright_green]")
        if user_input == "return":
            return
        show_error = True
        for user in users:
            if user.get("username") == user_input:
                user_object = view.get_object(**view.filter(username=user_input)[0])
                user_object.is_active = not user_object.is_active
                console.print(f"[bold cyan]{user_input} account changed to [/bold cyan]", end="")
                if user_object.is_active:
                    console.print("[bold green]Active[/bold green]")
                    log.info(f"{user_input} account activated.")
                else:
                    console.print("[bold red]Blocked[/bold red]")
                    log.info(f"{user_input} account blocked.")

                user_object.save()
                show_error = False
        if show_error:
            console.print("[bold red]There is no user with this username.[/bold red]")


def project_environment(project_id: str) -> None:
    """
    show the project environment
    :param project_id: str
    :return: None
    """
    project_view = ProjectViewSet()
    user_project_view = UserProjectViewSet()
    view = UserViewSet()
    table = Table()
    table.add_column("Field", justify="full", style="cyan")
    table.add_column("Value", justify="full", style="chartreuse1")
    table.add_row("Title", project_view.filter(id=project_id)[0].get("title"))
    table.add_row("Leader", view.filter(id=project_view.filter(id=project_id)[0].get("leader_id"))[0].get("username"))
    table.add_row("Users", "")
    users = user_project_view.filter(project_id=project_id)
    for user in users:
        table.add_row("", view.filter(id=user.get("user_id"))[0].get("username"))
    print(table)


def delete_user(user_id: str, project_id: str) -> None:
    """
    delete user from project with project id
    :param user_id: str
    :param project_id: str
    :return: None
    """
    user_project_view = UserProjectViewSet()
    view = UserViewSet()
    project_view = ProjectViewSet()
    while True:
        users = user_project_view.filter(project_id=project_id)
        table = Table(title="Users")
        table.add_column("Users", justify="full", style="cyan", no_wrap=True)
        for user in users:
            table.add_row(view.filter(id=user.get("user_id"))[0].get("username"))
        console.print(table)
        member = console.input("[bright_green]Enter username to delete :[/bright_green]")
        if member == "return":
            return
        is_ok = False
        for user in users:
            target_user_id = user.get("user_id")
            if member == view.filter(id=target_user_id)[0].get("username"):
                is_ok = True
                if target_user_id != project_view.filter(id=project_id)[0].get("leader_id"):
                    user_project_view.delete(user_id=target_user_id, project_id=project_id)
                    log.info(f"{view.filter(id=target_user_id)[0].get("username")} deleted from {project_view.filter(id=project_id)[0].get("title")}.")
                else:
                    console.print("[bold red]leader can`t be removed, you can delete project from menu.[/bold red]")
        if not is_ok:
            console.print("[bold red]There is no user with this username in project.[/bold red]")


def delete_project(user_id: str, project_id: str):
    """
    delete project with project id
    :param user_id: str
    :param project_id: str
    :return: None
    """
    view = ProjectViewSet()
    log.info(f"{view.filter(id=project_id)[0].get("title")} deleted.")
    view.delete(id=project_id)


def show_history(user_id: str, project_id: str, task_id: str):
    """
    show history of task with task id
    :param user_id: str
    :param project_id: str
    :param task_id: str
    :return: None
    """
    task_view = TaskViewSet()
    user_view = UserViewSet()
    user_data = task_view.filter(id=task_id)[0]
    task: TaskModel = task_view.get_object(**user_data)
    data: list[dict] = task.show_history()
    index: int = 1
    username: str
    for history in data:
        username = user_view.filter(id=history.get("auther_id"))[0]["username"]
        console.print(f"{index} - the {username} changed the task at {history.get("created_at")}")
    history_index = int(console.input("Enter the number of option: ")) - 1
    history = data[history_index]
    table = Table()
    table.add_column("Number", justify="full", style="magenta")
    table.add_column("Field", justify="full", style="magenta")
    table.add_column("Base", justify="full", style="magenta")
    table.add_column("Changed", justify="full", style="magenta")
    table.add_row(
        "1", "Title", history.get("title", ("", ""))[0], history.get("title", ("", ""))[1]
    )
    table.add_row(
        "2", "Description", history.get("description", ("", ""))[0], history.get("description", ("", ""))[1]
    )
    table.add_row(
        "3", "Started at", history.get("started_at", ("", ""))[0], history.get("started_at", ("", ""))[1]
    )
    table.add_row(
        "4", "Finishes at", history.get("ended_at", ("", ""))[0], history.get("ended_at", ("", ""))[1]
    )
    table.add_row("5", "Users added", "", " ".join(history.get("users_added", ("", ""))))
    table.add_row("6", "Users removed", "", " ".join(history.get("users_deleted", ("", ""))))
    if priority := history.get("priority"):
        table.add_row(
            "7", "Priority",
            TaskModel.Priority(priority[0]).name,
            TaskModel.Priority(priority[1]).name
        )
    else:
        table.add_row(
            "7", "Priority", "", ""
        )
    if status := history.get("status"):
        table.add_row(
            "8", "Status",
            TaskModel.Status(status[0]).name,
            TaskModel.Status(status[1]).name
        )
    else:
        table.add_row(
            "8", "Status", "", ""
        )
    console.print(table)
    console.input("[cyan]Press enter to continue.[/cyan]")


def show_task(user_id: str, project_id: str, task_id: str):
    """
    show the details of the task with task id
    :param user_id: str
    :param project_id: str
    :param task_id: str
    :return: None
    """
    user_view = UserViewSet()
    task_view = TaskViewSet()
    task = task_view.filter(id=task_id)[0]
    users_in_task = TaskModel.from_data(TaskModel.Meta.adapter.get(task_id)).get_members()
    table = Table()
    table.add_column("Field", justify="full", style="chartreuse1")
    table.add_column("Value", justify="full", style="magenta")
    table.add_row("title", task.get("title"))
    table.add_row("Description", task.get("description"))
    table.add_row("Started at", task.get("started_at"))
    table.add_row("Finishes at", task.get("ended_at"))
    table.add_row("Assignees", "")
    for user in users_in_task:
        table.add_row( "", user_view.filter(id=user)[0].get("username"))
    table.add_row("priority", TaskModel.Priority(task.get("priority")).name)
    table.add_row("status", TaskModel.Status(task.get("status")).name)
    console.print(table)


def update_task(user_id: str, project_id: str, task_id: str):
    """
    update the task with task id
    :param user_id: str
    :param project_id: str
    :param task_id: str
    :return: None
    """
    user_view = UserViewSet()
    project_view = ProjectViewSet()
    task_view = TaskViewSet()
    user_project_view = UserProjectViewSet()
    task = task_view.filter(id=task_id)[0]
    changed_task: TaskModel = TaskModel.from_data(TaskModel.Meta.adapter.get(task_id))
    users_in_task = TaskModel.from_data(TaskModel.Meta.adapter.get(task_id)).get_members()
    users_in_task_id = changed_task.get_members()
    while True:
        table = Table()
        table.add_column("Number", justify="full", style="cyan")
        table.add_column("Field", justify="full", style="chartreuse1")
        table.add_column("Base", justify="full", style="medium_purple3")
        table.add_column("Changed", justify="full", style="light_green")
        table.add_row("1", "title", task.get("title"), changed_task.title)
        table.add_row("2", "Description", task.get("description"), changed_task.description)
        table.add_row("3", "Started at", task.get("started_at"), str(changed_task.started_at))
        table.add_row("4", "Finishes at", task.get("ended_at"), str(changed_task.ended_at))
        table.add_row("5", "Assignees", "")
        for i in range(max(len(users_in_task), len(users_in_task_id))):
            if len(users_in_task) >= i+1 > len(users_in_task_id):
                table.add_row("", "", user_view.filter(id=users_in_task[i])[0].get("username"), "")
            elif len(users_in_task_id) >= i+1 > len(users_in_task):
                table.add_row("", "", "", user_view.filter(id=users_in_task_id[i])[0].get("username"))
            else:
                table.add_row("", "", user_view.filter(id=users_in_task[i])[0].get("username"),
                              user_view.filter(id=users_in_task_id[i])[0].get("username"))
        table.add_row("6", "priority", TaskModel.Priority(task.get("priority")).name,
                      TaskModel.Priority(changed_task.priority).name)
        table.add_row("7", "status", TaskModel.Status(task.get("status")).name,
                      TaskModel.Status(changed_task.status).name)
        console.print(table)
        member_number: int
        while True:
            member_number_str = console.input("[bright_green]Enter Field number to change : [/bright_green]")
            if member_number_str == "return":
                return
            elif member_number_str == "save":
                log.info(f"{user_view.filter(id=user_id)[0].get("username")} changed {task_view.filter(id=task_id)[0].get("title")} in {project_view.filter(id=project_id)[0].get("title")}.")
                changed_task.save()
                return
            elif is_number(member_number_str):
                member_number = int(member_number_str)
                break
            else:
                console.print("[bold red]Invalid input[/bold red]")

        if project_view.filter(id=project_id)[0].get("leader_id") == user_id:

            if int(member_number) == 1:
                changed_task.title = console.input("[bright_green]Enter new title : [/bright_green]")

            elif int(member_number) == 3:
                while True:
                    _input = console.input("[bright_green]Enter start date and time: [/bright_green]")
                    if validate_date(_input):
                        input_time = Date.from_string(_input)
                        if input_time.time.timestamp() > changed_task.ended_at.time.timestamp():
                            console.print("[bold red]Invalid time.[/bold red]")
                        else:
                            changed_task.started_at = input_time
                            break
                    else:
                        console.print("[bold red]Invalid format.[/bold red]")
            elif int(member_number) == 4:
                _input = console.input("[bright_green]Enter end date and time: [/bright_green]")
                if validate_date(_input):
                    input_time = Date.from_string(_input)
                    if changed_task.started_at.time.timestamp() > input_time.time.timestamp():
                        console.print("[bold red]Invalid time.[/bold red]")
                    else:
                        changed_task.ended_at = input_time
                        break
                else:
                    console.print("[bold red]Invalid format.[/bold red]")
            elif int(member_number) == 5:
                users_in_project = user_project_view.filter(project_id=project_id)
                while True:
                    table = Table(title="Users")
                    table.add_column("Users", justify="full", style="cyan", no_wrap=True)
                    table.add_column("Users who are not in task", justify="full", style="red", no_wrap=True)
                    table.add_column("Users who are in task", justify="full", style="green", no_wrap=True)
                    for user in users_in_project:
                        is_in_task = False
                        for id in users_in_task_id:
                            if id == user.get("user_id"):
                                is_in_task = True
                        if not is_in_task:
                            table.add_row(user_view.filter(id=user.get("user_id"))[0].get("username"),
                                          user_view.filter(id=user.get("user_id"))[0].get("username"), "")
                        else:
                            table.add_row(user_view.filter(id=user.get("user_id"))[0].get("username"), "",
                                          user_view.filter(id=user.get("user_id"))[0].get("username"))
                    console.print(table)

                    member_username = console.input("[bright_green]Enter the username of member: [/bright_green]")
                    if member_username == "return":
                        break
                    if members := user_view.filter(username=member_username):
                        member_id = members[0].get("id")
                        for user in users_in_project:
                            if user.get("user_id") == member_id:
                                is_in_task = False
                                for id in users_in_task_id:
                                    if member_id == id:
                                        is_in_task = True
                                if not is_in_task:
                                    changed_task.add_member(member_id=member_id)
                                    users_in_task_id.append(member_id)
                                    log.info(f"{user_view.filter(id=user_id)[0].get("username")} added {user_view.filter(id=member_id)[0].get("username")} to {task_view.filter(id=task_id)[0].get("title")} in {project_view.filter(id=project_id)[0].get("title")}.")

                                else:
                                    changed_task.remove_member(member_id=member_id)
                                    users_in_task_id.remove(member_id)
                                    log.info(f"{user_view.filter(id=user_id)[0].get("username")} deleted {user_view.filter(id=member_id)[0].get("username")} from {task_view.filter(id=task_id)[0].get("title")} in {project_view.filter(id=project_id)[0].get("title")}.")

                    else:
                        console.print("[bold red]There is no user with this username.[/bold red]")
        if int(member_number) == 6:
            for i in range(1, 5):
                console.print(f"[bold cyan]{i} - {TaskModel.Priority(i).name}[/bold cyan]")
            while True:
                _input = console.input("[bold cyan]Enter priority number: [/bold cyan]")
                if is_number(_input):
                    if 1 <= int(_input) <= 4:
                        changed_task.priority = TaskModel.Priority(int(_input))
                        break
                    else:
                        console.print("[bold red]Invalid number.[/bold red]")
                else:
                    console.print("[bold red]Invalid input. [/bold red]")

        if int(member_number) == 7:
            for i in range(1, 6):
                console.print(f"[bold cyan]{i} - {TaskModel.Status(i).name}[/bold cyan]")
            while True:
                _input = console.input("[bold cyan]Enter status number: [/bold cyan]")
                if is_number(_input):
                    if 1 <= int(_input) <= 5:
                        changed_task.status = TaskModel.Status(int(_input))
                        break
                    else:
                        console.print("[bold red]Invalid number.[/bold red]")
                else:
                    console.print("[bold red]Invalid input.[/bold red]")

        if int(member_number) == 2:
            changed_task.description = console.input("[bright_green]Enter new description : [/bright_green]")

        if int(member_number) == 0:
            return


def show_task_options(user_id: str, project_id: str, task_id: str):
    """
    show the options of task
    :param user_id: str
    :param project_id: str
    :param task_id: str
    :return: None
    """
    show_task(user_id, project_id, task_id)
    options = {
        "Update task": update_task,
        "Add comment": add_comment,
        "Show comments": show_comments,
        "Show history": show_history,
    }
    users_in_task = TaskModel.from_data(TaskModel.Meta.adapter.get(task_id)).get_members()
    options_list = list(options.keys())
    if not user_id in users_in_task:
        options_list.pop(0)

    table = Table(title="Options")
    table.add_column("Number", justify="full", style="cyan", no_wrap=True)
    table.add_column("Option", justify="full", style="chartreuse1")
    for index in range(len(options_list)):
        table.add_row(str(index + 1), options_list[index])
    console.print(table)
    user_input: int
    while True:
        _input = console.input("[bright_green]Enter your Option: [/bright_green]")
        if is_number(_input):
            if 0 <= int(_input) <= len(options_list):
                user_input = int(_input)-1
                break
            else:
                console.print("[bold red]Invalid number.[/bold red]")
        else:
            console.print("[bold red]Invalid input.[/bold red]")

    if user_input == -1:
        return
    func = options[options_list[user_input]]
    func(user_id, project_id, task_id)
    show_task_options(user_id, project_id, task_id)


def show_project_options(user_id: str, project_id: str):
    """
    show the options of project
    :param user_id: str
    :param project_id: str
    :return: None
    """
    project_view = ProjectViewSet()
    options = {
        "Show tasks": show_tasks,
        "Add task": add_task,
        "Delete users": delete_user,
        "Delete project": delete_project,
    }
    options_list = list(options.keys())
    if not user_id == project_view.filter(id=project_id)[0].get("leader_id"):
        options_list.pop(1)
        options_list.pop(1)
        options_list.pop(1)

    table = Table(title="Options")
    table.add_column("Number", justify="full", style="cyan", no_wrap=True)
    table.add_column("Option", justify="full", style="chartreuse1")
    for index in range(len(options_list)):
        table.add_row(str(index + 1), options_list[index])
    console.print(table)
    user_input: int
    while True:
        _input = console.input("[bright_green]Enter your Option: [/bright_green]")
        if is_number(_input):
            if 0 <= int(_input) <= len(options_list):
                user_input = int(_input)-1
                break
            else:
                console.print("[bold red]Invalid number.[/bold red]")
        else:
            console.print("[bold red]Invalid input.[/bold red]")

    if user_input == -1:
        return
    func = options[options_list[user_input]]
    func(user_id, project_id)
    if user_input == 3:
        return
    show_project_options(user_id, project_id)


def show_projects(user_id: str):
    """
    show the projects on database
    :param user_id: str
    :return: None
    """
    view = UserProjectViewSet()
    project_view = ProjectViewSet()
    user_projects_id = list()

    table = Table()
    table.add_column("Number", justify="full", style="cyan", no_wrap=True)
    table.add_column("Title", justify="full", style="chartreuse1")

    for project in list(filter(lambda item: item["leader_id"] == user_id, project_view.list())):
        user_projects_id.append(project.get("id"))
        table.add_row(str(len(user_projects_id)), project.get("title"), style="chartreuse1")
    projects = list(filter(lambda item: item["user_id"] == user_id, view.list()))
    for project in projects:
        is_ok = True
        for sub_project in list(filter(lambda item: item["leader_id"] == user_id, project_view.list())):
            if project.get("project_id") == sub_project.get("id"):
                is_ok = False
        if is_ok:
            user_projects_id.append(project.get("project_id"))
            table.add_row(str(len(user_projects_id)), project_view.filter(id=project.get("project_id"))[0].get("title"), style="cyan")
    print(table)

    user_input: int
    while True:
        _input = console.input("[bright_green]Enter number of project to open:[bright_green]")
        if is_number(_input):
            if 0 <= int(_input) <= len(user_projects_id):
                user_input = int(_input)
                break
            else:
                console.print("[bold red]Invalid number.[/bold red]")
        else:
            console.print("[bold red]Invalid input.[/bold red]")

    if user_input == 0:
        return
    project_environment(user_projects_id[user_input-1])
    show_project_options(user_id, user_projects_id[user_input-1])


def can_add(project_id: str, user_id: str, count: int) -> bool:
    """
    check the user can be added in project or cannot
    :param project_id: str
    :param user_id: str
    :param count: int
    :return: bool
    """
    user_view = UserViewSet()
    user_project_view = UserProjectViewSet()
    if username_exist(list(filter(lambda item: item["id"] == user_id, user_view.list()))[0].get("username"), user_view):
        users_in_project = list(filter(lambda item: item["project_id"] == project_id, user_project_view.list()))
        for i in range(count):
            if users_in_project[i].get("user_id") == user_id:
                console.print()
                return False
        return True
    return False


def title_exist(title: str) -> bool:
    """
    check the title is unique or not
    :param title: str
    :return: bool
    """
    project_view = ProjectViewSet()
    if len(list(filter(lambda item: item["title"] == title, project_view.list()))) == 0:
        return True
    return False


def add_project(user_id: str):
    """
    add the project in database
    :param user_id: str
    :return: None
    """
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
    log.info(f"{view.filter(id=user_id)[0].get("username")} created {title}.")

    project.add_member(member_id=user_id)

    members_count: int
    while True:
        _input = console.input("[bright_green]Enter your count of members: [/bright_green]")
        if is_number(_input):
            if 0 <= int(_input):
                members_count = int(_input)
                break
            else:
                console.print("[bold red]Invalid number.[/bold red]")
        else:
            console.print("[bold red]Invalid input.[/bold red]")
    index = 1
    while index < members_count + 1:
        member_username = console.input(f"[bright_green]{index} - Enter the username of member: [/bright_green]")
        if member_username == "return":
            return
        if not username_exist(member_username, view):
            console.print("[bold red]There is no user with this username.[/bold red]")
            continue
        member_id = list(filter(lambda item: item["username"] == member_username, view.list()))[0].get("id")
        if can_add(project.id, list(filter(lambda item: item["username"] == member_username, view.list()))[0].get("id"), index):
            project.add_member(member_id=member_id)
            log.info(f"{view.filter(id=user_id)[0].get("username")} added {member_username} to {title}.")
            index = index + 1
        else:
            console.print("[bold red]You cant add this user.[/bold red]")


def validate_date(date: str) -> bool:
    """
    check the date is valid or not (with regex)
    :param date: str
    :return: bool
    """
    pattern = r'\d{4}-\d?\d-\d?\d (?:2[0-3]|[01]?[0-9]):[0-5]?[0-9]:[0-5]?[0-9]'
    if re.fullmatch(pattern, date):
        now = Date(time=datetime.now())
        input_time = Date.from_string(date)
        if now.time.timestamp() > input_time.time.timestamp():
            return False
        return True
    return False


def add_task(user_id: str, project_id: str):
    """
    add the task in database
    :param user_id: str
    :param project_id: str
    :return: None
    """
    user_view = UserViewSet()
    project_view = ProjectViewSet()
    user_project_view = UserProjectViewSet()
    title = console.input("[bright_green]Enter task title: [/bright_green]")
    description = console.input("[bright_green]Enter your description: [/bright_green]")
    started_at: Date
    while True:
        if _input := console.input("[bright_green]Enter start date and time: [/bright_green]"):
            if validate_date(_input):
                started_at = Date.from_string(_input)
                break
            else:
                console.print("[bold red]Invalid format.[/bold red]")
        else:
            started_at = Date(time=datetime.now())
            break

    ended_at: Date
    while True:
        if _input := console.input("[bright_green]Enter end date and time: [/bright_green]"):
            if validate_date(_input):
                input_time = Date.from_string(_input)
                if started_at.time.timestamp() > input_time.time.timestamp():
                    console.print("[bold red]Invalid time.[/bold red]")
                else:
                    ended_at = Date.from_string(_input)
                    break
            else:
                console.print("[bold red]Invalid format[/bold red]")
        else:
            now = started_at.time
            ended_at = Date(time=now.replace(day=now.day+1))
            break

    for i in range(1, 5):
        console.print(f"[cyan]{i} - {TaskModel.Priority(i).name}[/cyan]")
    priority: int
    while True:
        if _input := console.input("[bright_green]Enter priority number: [/bright_green]"):
            if is_number(_input):
                if 1 <= int(_input) <= 4:
                    priority = int(_input)
                    break
                else:
                    console.print("[bold red]Invalid number.[/bold red]")
            else:
                console.print("[bold red]Invalid input[/bold red]")
        else:
            priority = 1
            break

    for i in range(1, 6):
        console.print(f"[cyan]{i} - {TaskModel.Status(i).name}[/cyan]")
    status: int
    while True:
        if _input := console.input("[bright_green]Enter status number: [/bright_green]"):
            if is_number(_input):
                if 1 <= int(_input) <= 5:
                    status = int(_input)
                    break
                else:
                    console.print("[bold red]Invalid number.[/bold red]")
            else:
                console.print("[bold red]Invalid input.[/bold red]")
        else:
            status = 1
            break

    task = TaskModel(title=title, project_id=project_id, description=description,
                     started_at=started_at, ended_at=ended_at,
                     priority=priority, status=status)
    task.save()
    log.info(f"{user_view.filter(id=user_id)[0].get("username")} added {title} to {project_view.filter(id=project_id)[0].get("title")}.")

    users_in_task_id = list()
    users_in_project = user_project_view.filter(project_id=project_id)
    while True:

        table = Table(title="Users")
        table.add_column("Users", justify="full", style="cyan", no_wrap=True)
        table.add_column("Users who are not in task", justify="full", style="red", no_wrap=True)
        table.add_column("Users who are in task", justify="full", style="green", no_wrap=True)
        for user in users_in_project:
            is_in_task = False
            for id in users_in_task_id:
                if id == user.get("user_id"):
                    is_in_task = True
            if not is_in_task:
                table.add_row(user_view.filter(id=user.get("user_id"))[0].get("username"), user_view.filter(id=user.get("user_id"))[0].get("username"), "")
            else:
                table.add_row(user_view.filter(id=user.get("user_id"))[0].get("username"), "", user_view.filter(id=user.get("user_id"))[0].get("username"))
        console.print(table)

        member_username = console.input(f"[bright_green]Enter the username of member: [/bright_green]")
        if member_username == "return":
            return
        if members := user_view.filter(username=member_username):
            member_id = members[0].get("id")
            for user in users_in_project:
                if user.get("user_id") == member_id:
                    is_in_task = False
                    for id in users_in_task_id:
                        if member_id == id:
                            is_in_task = True
                    if not is_in_task:
                        task.add_member(member_id=member_id)
                        log.info(f"{user_view.filter(id=user_id)[0].get("username")} added {member_username} to {title} in {project_view.filter(id=project_id)[0].get("title")}.")

                        users_in_task_id.append(member_id)
                    else:
                        task.remove_member(member_id=member_id)
                        log.info(f"{user_view.filter(id=user_id)[0].get("username")} deleted {member_username} from {title} in {project_view.filter(id=project_id)[0].get("title")}.")
                        users_in_task_id.remove(member_id)
        else:
            console.print("[bold red]There is no user with this username.[/bold red]")


def show_tasks(user_id: str, project_id: str):
    """
    show the tasks of the project with project id
    :param user_id: str
    :param project_id: str
    :return: None
    """
    view = TaskViewSet()
    tasks = view.filter(project_id=project_id)
    backlog_tasks = list()
    todo_tasks = list()
    doing_tasks = list()
    done_tasks = list()
    archived_tasks = list()
    for task in tasks:
        if task.get("status") == 1:
            backlog_tasks.append(task.get("title"))
        if task.get("status") == 2:
            todo_tasks.append(task.get("title"))
        if task.get("status") == 3:
            doing_tasks.append(task.get("title"))
        if task.get("status") == 4:
            done_tasks.append(task.get("title"))
        if task.get("status") == 5:
            archived_tasks.append(task.get("title"))
    max_row = max(len(backlog_tasks),len(todo_tasks),len(doing_tasks),len(done_tasks),len(archived_tasks))

    table = Table(title="Tasks")
    table.add_column("BACKLOG", justify="full", style="deep_pink4", no_wrap=True)
    table.add_column("TODO", justify="full", style="medium_purple1", no_wrap=True)
    table.add_column("DOING", justify="full", style="orange_red1", no_wrap=True)
    table.add_column("DONE", justify="full", style="yellow1", no_wrap=True)
    table.add_column("ARCHIVED", justify="full", style="chartreuse1", no_wrap=True)

    for i in range(max_row):
        temp_backlog_tasks: str
        temp_todo_tasks: str
        temp_doing_tasks: str
        temp_done_tasks: str
        temp_archived_tasks: str
        if i >= len(backlog_tasks):
            temp_backlog_tasks = ""
        else:
            temp_backlog_tasks = backlog_tasks[i]

        if i >= len(todo_tasks):
            temp_todo_tasks = ""
        else:
            temp_todo_tasks = todo_tasks[i]

        if i >= len(doing_tasks):
            temp_doing_tasks = ""
        else:
            temp_doing_tasks = doing_tasks[i]

        if i >= len(done_tasks):
            temp_done_tasks = ""
        else:
            temp_done_tasks = done_tasks[i]

        if i >= len(archived_tasks):
            temp_archived_tasks = ""
        else:
            temp_archived_tasks = archived_tasks[i]
        table.add_row(temp_backlog_tasks, temp_todo_tasks, temp_doing_tasks, temp_done_tasks, temp_archived_tasks)

    while True:
        console.print(table)
        member_input = console.input("[bright_green]Enter Task title :[/bright_green]")
        if member_input == "return":
            return
        for task in tasks:
            if task.get("title") == member_input:
                show_task_options(user_id, project_id, task.get("id"))


def add_comment(user_id: str, project_id: str, task_id: str):
    """
    add a comment in database with task id and user id
    :param user_id: str
    :param project_id: str
    :param task_id: str
    :return: None
    """
    user_view = UserViewSet()
    task_view = TaskViewSet()
    project_view = ProjectViewSet()
    text = console.input("[bright_green]Enter your text: [/bright_green]")
    log.info(f"{user_view.filter(id=user_id)[0].get("username")} added comment to {task_view.filter(id=task_id)[0].get("title")} in {project_view.filter(id=project_id)[0].get("title")}.")
    comment = CommentModel(task_id=task_id, text=text, user_id=user_id)
    comment.save()


def show_comments(user_id: str, project_id: str, task_id: str):
    """
    show the comments of the task with task id
    :param user_id: str
    :param project_id: str
    :param task_id: str
    :return: None
    """
    view = CommentViewSet()
    user_view = UserViewSet()
    comments = view.filter(task_id=task_id)
    table = Table(title="COMMENTS")
    table.add_column("Date", justify="full", style="cyan", no_wrap=True)
    table.add_column("Writer", justify="full", style="plum1", no_wrap=True)
    table.add_column("Text", justify="full", style="green", no_wrap=True)
    for comment in comments:
        table.add_row(comment.get("created_at"), user_view.filter(id=comment.get("user_id"))[0].get("username"), comment.get("text"))
    print(table)
    console.input("[cyan]Press enter to continue[/cyan]")


def show_logs(user_id: str):
    """
    show the all logs
    :param user_id: str
    :return: None
    """
    console.print("[cyan]LOGS[/cyan]")
    logs: list = []
    with open(ROOT_DIR.joinpath("database").joinpath("logs.txt").resolve(), "r", encoding="utf-8") as f:
        logs = f.readlines()
    logs.reverse()
    for log in logs:
        print(f"[sea_green1]{log[:-1]}[/sea_green1]")


def show_menu(_type: str, user_id: str):
    """
    show the options of activity for user
    :param _type: str
    :param user_id: str
    :return: None
    """
    view = UserViewSet()
    options = {
        "Show logs": show_logs,
        "Sign Up": sign_up,
        "Log in": log_in,
        "Change users activity": users_activity,
        "Show projects": show_projects,
        "Add project": add_project
    }
    options_list = list(options.keys())
    if _type == "main":
        options_list.pop(0)
        options_list.pop(2)
        options_list.pop(2)
        options_list.pop(2)
    elif not list(filter(lambda item: item["id"] == user_id, view.list()))[0].get("is_admin"):
        for i in range(4):
            options_list.pop(0)
    else:
        for i in range(2):
            options_list.pop(1)

    table = Table(title="Options")
    table.add_column("Number", justify="full", style="chartreuse1", no_wrap=True)
    table.add_column("Option", justify="full", style="purple")

    for index in range(len(options_list)):
        table.add_row(str(index + 1), options_list[index])
    console.print(table)

    user_input: int
    _input: str
    while True:
        _input = console.input("[bright_green]Enter your Option: [/bright_green]")
        if is_number(_input):
            if 0 <= int(_input) <= len(options_list):
                user_input = int(_input)-1
                break
            else:
                console.print("[bold red]Invalid number.[/bold red]")
        else:
            console.print("[bold red]Invalid input.[/bold red]")

    if user_input == -1:
        return
    func = options[options_list[user_input]]
    func(user_id)
    show_menu(_type, user_id)


def main():
    show_menu("main", "0")


if __name__ == "__main__":
    pretty.install()
    console = Console()
    main()
