import argparse
import sys
from pprint import pprint
from office.views import UserViewSet
from main import username_exist


def add_user(**kwargs):
    view = UserViewSet()
    pprint(view.create(kwargs))


commands = {
    "create-admin": add_user,
}


def purge():
    pass


def main():
    view = UserViewSet()
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("-u", "--username")
    parser.add_argument("--password")
    args = parser.parse_args(sys.argv[1:]).__dict__
    args["is_admin"] = True
    args["email"] = "admin_test@gmail.com"
    if username_exist(args.get("username"), view):
        if not list(filter(lambda item: item["username"] == args.get("username"), view.list()["objects"]))[0].get("is_admin"):
            print(f"User {args.get("username")} is now admin. ")
        else:
            print("There is a admin with this username.")
    else:
        func = commands[args.pop("target")]
        func(**args)
        print("Admin creation was successful.")
    purge()


if __name__ == "__main__":
    main()
