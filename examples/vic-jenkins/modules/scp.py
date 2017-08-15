import cmd
import os

import shutil

import paramiko
from paramiko import SSHClient
from scp import SCPClient


def progress(filename, size, sent):
    print(filename, size, sent)


def get_files_wrapper(**kwargs) -> bool:
    vch_hostname = os.environ["HOSTNAME"]
    source = os.environ["SOURCE"]
    destination = os.environ["DESTINATION"]
    username = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]

    get_files(vch_hostname, source, destination, username, password)


def get_files(hostname, source, destination, username, password):
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.connect(hostname, port=22, username=username, password=password)

    # SCPCLient takes a paramiko transport as its only argument
    # Just a no-op. Required sanitize function to allow wildcards.
    scp = SCPClient(ssh.get_transport(), sanitize=lambda x: x, progress=progress)

    if not os.path.exists(destination):
        os.makedirs(destination)

    scp.get(source, destination, recursive=True)
