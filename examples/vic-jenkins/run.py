import os
import sys

import logging
import urllib3
from modules import vicmachine

from modules import jenkins

try:
    import settings_local as settings
    print("Imported local settings.")
except ImportError:
    import settings
    print("Imported default settings.")

# Disable SSL warnings. I know. I don't care.
urllib3.disable_warnings()


def parse_command(args):
    verb = args[0]

    if verb == "create":
        target = args[1]

        if target == "vic":
            vicmachine.deploy(settings)

        elif target == "jenkins":
            target = args[2]

            docker_url, cert_path = vicmachine.load_config(settings)

            if docker_url is not None and cert_path is not None:

                if target == "master" or target == "all":
                    jenkins.master.build_master(settings)

                    if jenkins.master.deploy_master(settings, docker_url, cert_path):
                        print("Successfully deployed jenkins master")
                    else:
                        print("Failed to deploy jenkins master")

                if target == "slave" or target == "all":
                    jenkins.slave.build_slave(settings)
                    jenkins.slave.deploy_slave(settings, docker_url, cert_path)

    elif verb == "configure":
        target = args[1]

        if target == "jenkins":
            target = args[2]

            if target == "master" or target == "all":
                docker_url, cert_path = vicmachine.load_config(settings)

                jenkins.master.configure_master(settings, docker_url, cert_path)

            elif target == "slave" or target == "all":
                pass

    elif verb == "delete":
        if vicmachine.delete(settings):
            print("Successfully deleted VCH")
        else:
            print("Failed to delete VCH")


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