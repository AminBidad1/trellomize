import argparse
import sys
from office.views import add_user

commands = {
    "create-admin": add_user,
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
