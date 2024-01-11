#!/usr/bin/env python3

import subprocess
import getpass
import time
import pdb
import configparser
import sys
import logging

import requests

def parse_config(path):
    config = configparser.ConfigParser()
    try:
        config.read(path)

        emitter = config['emitters']['emitter']
        if emitter == '':
            logging.critical("Missing emitter type.")
            sys.exit()
        elif str.lower(emitter) != 'email' and str.lower(emitter) != 'telegram':
            logging.critical("Emitter type must be either email or telegram.")
            sys.exit()
    except KeyError:
        logging.critical("Please check /etc/zypper-automatic.conf")
        sys.exit()

    return config

def check_root():
    if getpass.getuser() != "root":
        logging.critical("Must be root to execute zypper commands.")
        sys.exit()

def refresh_repos():
    for i in range(0, 2):
        try:
            logging.info("Refreshing repositories...")
            output = subprocess.check_output(["zypper", "refresh"])
            err = None
            break
        except subprocess.CalledProcessError as e:
            err = e
            time.sleep(300)
            continue
    else:
        logging.warning("An error occured while refreshing repos. See output below.")
        print(err.output)
        output = err.output
    
    return output

def list_patches():
    try:
        logging.info("Retrieving list of all patches...")
        output = subprocess.check_output(["zypper", "list-patches"])
    except subprocess.CalledProcessError as err:
        logging.warning("An error occured while listing patches. See output below.")
        print(err.output)
        output = err.output
    
    return output

def install_patches(categories, with_interactive):
    command = ["zypper", "patch", "--no-confirm", "--details"]

    if categories != '':
        categories_list = categories.replace(" ", "").split(',')
        for c in categories_list:
            if "--category" not in command:
                command.append("--category")
            if str.lower(c) == "security":
                command.append("security")
            if str.lower(c) == "recommended":
                command.append("recommended")
            if str.lower(c) == "optional":
                command.append("optional")
            if str.lower(c) == "feature":
                command.append("feature")
            if str.lower(c) == "document":
                command.append("document")
            if str.lower(c) == "yast":
                command.append("yast")
    else:
        logging.warning("No categories specified. All patches will be installed.")

    if str.lower(with_interactive) == "true":
        command.append("--with-interactive")

    try:
        logging.info("Installing patches...")
        output = subprocess.check_output(command)
    except subprocess.CalledProcessError as err:
        if err.returncode == 102:
            logging.info("Reboot required.")
            output = err.output
        else:
            logging.warning("An error occured while installing patches. See output below.")
            print(err.output)
    
    return output

def send_email(content, subject, email_to):
    message = subprocess.Popen(["echo", content], stdout=subprocess.PIPE)
    command = subprocess.Popen(["mail", "-s", subject, email_to],
                                stdin=message.stdout,
                                stdout=subprocess.PIPE)
    message.stdout.close()
    logging.info("Sending email...")
    output = command.communicate()[0]
    return output

def send_telegram(content, token, chat_id):
    url = f'https://api.telegram.org/bot{token}/sendMessage?text={content}&chat_id={chat_id}'
    logging.info("Sending Telegram message...")
    r = requests.get(url)
    return r

def compose_body(time_start, refresh_output, install_output, list_output):
    if install_output == None:
        outputs = {'refresh_output': refresh_output,
                   'list_output': list_output}
    else:
        outputs = {'refresh_output': refresh_output,
                   'install_output': install_output,
                   'list_output': list_output}
    
    # Convert bytes to strings if needed.
    for key, value in outputs.items():
        if type(value) is bytes:
            outputs[key] = str(value, 'utf-8')
    
    head = f"JOB STARTED: {time_start}"
    
    # Combine outputs to create body of message.
    body = "\n".join(outputs.values())
    
    return body

if __name__ == "__main__":
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

    # Root is required in order to run zypper
    check_root()

    config = parse_config('/etc/zypper-automatic.conf')

    categories = config['zypper']['patch_categories']
    with_interactive = config['zypper']['with_interactive']
    list_only = config['zypper']['list_only']

    emitter = config['emitters']['emitter']
    email_to = config['email']['email_to']
    token = config['telegram']['token']
    chat_id = config['telegram']['chat_id']

    time_start = time.asctime(time.localtime(time.time()))

    refresh_output = refresh_repos()

    if str.lower(list_only) != "true":
        install_output = install_patches(categories, with_interactive)
    else:
        install_output = None

    list_output = list_patches()

    body = compose_body(time_start, refresh_output, install_output, list_output)

    # For emails only
    subject = "zypper-automatic"

    if str.lower(emitter) == 'email':
        send_email(body, subject, email_to)
    elif str.lower(emitter) == 'telegram':
        send_telegram(body, token, chat_id)
