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

        emitter = config['EMITTERS']['EMITTER']
        if emitter == '':
            logging.critical("Missing EMITTER type.")
            sys.exit()
        elif str.upper(emitter) != 'EMAIL' and str.upper(emitter) != 'TELEGRAM':
            logging.critical("EMITTER type must be either EMAIL or TELEGRAM.")
            sys.exit()
    except KeyError:
        logging.critical("Please check /etc/zypper-automatic.ini")
        sys.exit()

    return config

def check_root():
    if getpass.getuser() != "root":
        logging.critical("Must be root to execute zypper commands.")
        sys.exit()

def refresh_repos():
    logging.info("Refreshing repositories...")
    for i in range(0, 2):
        while True:
            try:
                output = subprocess.check_output(["zypper", "refresh"])
            except CalledProcessError:
                time.sleep(300)
                continue
            return output
    else:
        logging.warning("An error occured while refreshing repos. See output below.")
        print(err.output)
        output = err.output
    
    return output

def list_patches():
    logging.info("Retrieving list of all patches...")
    try:
        output = subprocess.check_output(["zypper", "list-patches"])
    except subprocess.CalledProcessError as err:
        logging.warning("An error occured while listing patches. See output below.")
        print(err.output)
        output = err.output
    
    return output

def install_patches(categories, with_interactive):
    logging.info("Installing patches...")
    command = ["zypper", "patch", "--no-confirm", "--details"]

    if categories != '':
        categories_list = categories.split(',')
        for c in categories_list:
            if "--category" not in command:
                command.append("--category")
            if str.upper(c) == "SECURITY":
                command.append("security")
            if str.upper(c) == "RECOMMENDED":
                command.append("recommended")
            if str.upper(c) == "OPTIONAL":
                command.append("optional")
            if str.upper(c) == "FEATURE":
                command.append("feature")
            if str.upper(c) == "DOCUMENT":
                command.append("document")
            if str.upper(c) == "YAST":
                command.append("yast")
    else:
        logging.warning("No categories specified. All patches will be installed."

    if upper(with_interactive) == "TRUE":
        command.append("--with-interactive")

    try:
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
    print("Sending email...")
    message = subprocess.Popen(["echo", content], stdout=subprocess.PIPE)
    command = subprocess.Popen(["mail", "-s", subject, email_to],
                                stdin=message.stdout,
                                stdout=subprocess.PIPE)
    message.stdout.close()
    output = command.communicate()[0]
    return output

def send_telegram(content, token, chat_id):
    logging.info("Sending Telegram message...")
    url = f'https://api.telegram.org/bot{token}/sendMessage?text={content}&chat_id={chat_id}'
    r = requests.get(url)
    return r

def compose_body(time_start, refresh_output, install_output, list_output):
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

    config = parse_config('/etc/zypper-automatic.ini')

    categories = config['ZYPPER']['PATCH_CATEGORIES']
    with_interactive = config['ZYPPER']['WITH_INTERACTIVE']

    emitter = config['EMITTERS']['EMITTER']
    email_to = config['EMAIL']['EMAIL_TO']
    token = config['TELEGRAM']['TOKEN']
    chat_id = config['TELEGRAM']['CHAT_ID']

    time_start = time.asctime(time.localtime(time.time()))

    refresh_output = refresh_repos()
    install_output = install_patches(categories, with_interactive)
    list_output = list_patches()

    body = compose_body(time_start, refresh_output, install_output, list_output)

    # For emails only
    subject = "zypper-automatic"

    if str.upper(emitter) == 'EMAIL':
        send_email(body, subject, email_to)
    elif str.upper(emitter) == 'TELEGRAM':
        send_telegram(body, token, chat_id)
