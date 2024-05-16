from pprint import pprint
from office.views import UserViewSet, ProjectViewSet
from office.models import UserModel, ProjectModel


def show_users():
    view = UserViewSet()
    pprint(view.list())


def show_projects():
    view = ProjectViewSet()
    pprint(view.list())


def add_project():
    username = input("Enter your username: ")
    if users := UserModel.Meta.adapter.filter(username=username):
        user_id = users[0].get("id")
        title = input("Enter your title: ")
        project = ProjectModel(title=title, leader_id=user_id)
        project.save()
    else:
        print("the input is not valid.")


def show_menu():
    options = {
        "Show users": show_users,
        "Show projects": show_projects,
        "Add project": add_project,
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
    main()
