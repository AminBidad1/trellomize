import argparse
import sys
from pprint import pprint
from office.views import UserViewSet
from libs.json_adapter import JsonAdapter
from settings import ROOT_DIR
from main import username_exist


def add_user(**kwargs):
    view = UserViewSet()
    pprint(view.create(kwargs))


def purge(**kwargs):
    JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_project.json").resolve()).purge()
    JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_task.json").resolve()).purge()
    JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_user.json").resolve()).purge()
    JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_user_project.json").resolve()).purge()
    JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_user_task.json").resolve()).purge()
    JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_comment.json").resolve()).purge()
    JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_history.json").resolve()).purge()
    with open(ROOT_DIR.joinpath("database").joinpath("logs.txt").resolve(), "w") as f:
        f.write("")


commands = {
    "create-admin": add_user,
    "purge-data": purge,
}


def main():
    view = UserViewSet()
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("-u", "--username", default=None)
    parser.add_argument("--password", default=None)
    args = parser.parse_args(sys.argv[1:]).__dict__
    args["is_admin"] = True
    args["email"] = "admin_test@gmail.com"
    if args.get("target") == "create-admin":
        if username_exist(args.get("username"), view):
            if not list(filter(lambda item: item["username"] == args.get("username"), view.list()["objects"]))[0].get("is_admin"):
                print(f"User {args.get("username")} is now admin. ")
            else:
                print("There is a admin with this username.")
        else:
            func = commands[args.pop("target")]
            func(**args)
            print("Admin creation was successful.")
    elif args.get("target") == "purge-data":
        if input("Are you sure ? [Y/N]") == "Y":
            purge()
            print("Deleting data was successful.")


if __name__ == "__main__":
    main()
