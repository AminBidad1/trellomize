import argparse
import sys
from pprint import pprint
from office.views import UserViewSet
from libs.json_adapter import JsonAdapter
from settings import ROOT_DIR


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
    with open(ROOT_DIR.joinpath("database").joinpath("logs.txt").resolve(), "w") as f:
        f.write("")


commands = {
    "create-admin": add_user,
    "purge-data": purge,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("-u", "--username")
    args = parser.parse_args(sys.argv[1:]).__dict__
    func = commands[args.pop("target")]
    func(**args)


if __name__ == "__main__":
    main()
