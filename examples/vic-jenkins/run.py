import os
import sys

import logging

import itertools
import urllib3

import modules
from modules import vicmachine

try:
    import settings_local as settings
    print("Imported local settings.")
except ImportError:
    import settings
    print("Imported default settings.")

# Disable SSL warnings. I know. I don't care.
urllib3.disable_warnings()


def parse_command(args):
    module = modules.MODULE

    for i, arg in enumerate(args[:-1]):
        if arg in module:
            module = module[arg]
        else:
            path = ".".join(args[:i+1])
            print("Could not find module with path:", path)
            return

    commands = args[-1].split("+")

    for command in commands:
        path = ".".join(itertools.chain(args[:-1], [command]))

        if command in module:
            command = module[command]
        else:
            print("Could not find command with path:", path)
            return

        if callable(command):
            print("Executing:", path)
            docker_url, cert_path = vicmachine.load_config(settings)

            function_args = {}

            if docker_url is not None:
                function_args["docker_url"] = docker_url

            if cert_path is not None:
                function_args["cert_path"] = cert_path

            return_val = command(settings, **function_args)

            if return_val:
                print()
                print("-----------------------------------------------------------------------------------------------")
                print("Successfully executed:", path)
                print("-----------------------------------------------------------------------------------------------")
                print()
            else:
                print()
                print("-----------------------------------------------------------------------------------------------")
                print("Error executing:", path)
                print("-----------------------------------------------------------------------------------------------")
                print()
                return

        else:
            print("Command not callable:", path)
            return


if __name__ == '__main__':
    verb = sys.argv[1]

    if "VERBOSE" in os.environ and os.environ["VERBOSE"].lower() == "true":
        logging.basicConfig(level=logging.DEBUG)

    if verb == "repl":
        while True:
            command = input("> ")
            parse_command(command.split())
    else:
        parse_command(sys.argv[1:])