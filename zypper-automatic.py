#!/usr/bin/env python3

import subprocess
import getpass
import time
import pdb
import configparser
import sys
import requests

ERROR = "\033[91m" + "[ERROR]" + "\033[0m"

def parse_config(path):
    config = configparser.ConfigParser()
    try:
        config.read(path)

        emitter = config['EMITTER']['EMITTER']
        if emitter == '':
            sys.exit(f"{ERROR} Missing EMITTER type.")
        elif str.upper(emitter) != 'EMAIL' and str.upper(emitter) != 'TELEGRAM':
            sys.exit(f"{ERROR} EMITTER type must be either EMAIL or TELEGRAM.")
    except KeyError:
        sys.exit(f"{ERROR} Please check /etc/zypper-automatic.ini")

    return config

def check_root():
    if getpass.getuser() != "root":
        raise RuntimeError("must be root to execute zypper commands.")

def refresh_repos():
    print("Refreshing repositories...")
    for i in range(0, 2):
        while True:
            try:
                output = subprocess.check_output(["zypper", "refresh"])
            except CalledProcessError:
                time.sleep(300)
                continue
            return output
    else:
        print("An error occured while refreshing repos.")
        print("See output below.")
        print(err.output)
        output = err.output
    
    return output

def list_patches():
    print("Retrieving list of all patches...")
    try:
        output = subprocess.check_output(["zypper", "list-patches"])
    except subprocess.CalledProcessError as err:
        print("An error occured while listing patches.")
        print("See output below.")
        print(err.output)
        output = err.output
    
    return output

def install_patches():
    print("Installing patches...")
    try:
        output = subprocess.check_output(["zypper", "patch",
                                          "--category", "security",
                                          "--no-confirm",
                                          "--with-interactive",
                                          "--details"])
    except subprocess.CalledProcessError as err:
        if err.returncode == 102:
            print("Reboot required.")
            output = err.output
        else:
            print("An error occured while installing patches.")
            print("See output below.")
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
    print("Sending Telegram message...")
    url = f'https://api.telegram.org/bot{token}/sendMessage?text{content}&chat_id={chat_id}'
    r = requests.get(url)
    return r

def compose_body(time_start):
    ref_out = refresh_repos()
    ins_out = install_patches()
    lis_out = list_patches()
    
    outputs = {'ref_out': ref_out, 'ins_out': ins_out, 'lis_out': lis_out}
    
    # Convert bytes to strings if needed.
    for key, value in outputs.items():
        if type(value) is bytes:
            outputs[key] = str(value, 'utf-8')
    
    head = f"JOB STARTED: {time_start}"
    
    # Combine outputs to create body of message.
    body = "\n".join(outputs.values())
    
    return body

if __name__ == "__main__":
    check_root()

    time_start = time.asctime(time.localtime(time.time()))
    body = compose_body(time_start)

    subject = "zypper-automatic"
    config = parse_config('/etc/zypper-automatic.ini')

    emitter = config['EMITTER']['EMITTER']
    email_to = config['EMAIL']['EMAIL_TO']
    token = config['TELEGRAM']['TOKEN']
    chat_id = config['TELEGRAM']['CHAT_ID']

    if str.upper(emitter) == 'EMAIL':
        send_email(body, subject, email_to)
    elif str.upper(emitter) == 'TELEGRAM':
        send_telegram(body, token, chat_id)
