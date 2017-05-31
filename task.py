#!/usr/bin/env python3

import hvac
import logging
import os
import paramiko
import re
import sys

from paramiko import SSHClient


def confirm_github_connection():
    """Confirm that the user can connect to github.
    """
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect('github.com', username='git')
        client.close()
    except Exception:
        print("Connection failed!")
        raise


def fetch_ssh_key(vault_url, vault_token):
    """Fetch SSH key from Vault server.

    :param vault_url: The url of the Vault server.
    :param vault_token: The token used to authenticate with Vault.
    """
    client = hvac.Client(url=vault_url, token=vault_token)
    data = client.read('infra-utils/iron-dev')
    ssh_key = data['data']['ssh-key']
    return ssh_key


def setup_logger(level=logging.ERROR):
    """Setup the basic logging config.

    :param level: The minimum level for log messages.
    """
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stderr))
    logger.setLevel(level)


def write_ssh_key(path, data, key_type=None):
    """Write a SSH key to disk.

    :param path: The path to the store the SSH key in.
    :param data: The SSH key data to be written.
    :param type: The type of SSH key.
    :return: The path to the key file.
    :rtype: str.
    """
    os.makedirs(path, 0o700)

    if not key_type:
        pattern = '-----BEGIN ([^ ]+) PRIVATE KEY-----'
        matches = re.match(pattern, data)
        if not matches:
            raise Exception('Unknown key type.')

        key_type = matches.group(1).lower()

    if key_type == 'ec':
        key_type = 'ecdsa'

    ssh_key_file = '{}/id_{}'.format(path, key_type)

    fp = open(ssh_key_file, 'w', 0o600)
    fp.write(data)
    fp.close()


def main():
    vault_url = os.environ.get('VAULT_URL', 'http://172.17.0.4:8200')
    vault_token = os.environ.get('VAULT_TOKEN', 'token')

    ssh_path = os.path.expanduser('~/.ssh')
    ssh_key = fetch_ssh_key(vault_url, vault_token)
    write_ssh_key(ssh_path, ssh_key)

    confirm_github_connection()


if __name__ == '__main__':
    setup_logger()
    try:
        main()
    except Exception as exp:
        logging.exception(exp)
        exit(1)

    print("Authentication successful.")