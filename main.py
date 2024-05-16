from pprint import pprint
from office.views import UserViewSet


def show_users():
    view = UserViewSet()
    pprint(view.list())


def show_menu():
    options = {
        "Show users": show_users
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
