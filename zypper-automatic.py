#!/usr/bin/env python3

import subprocess
import getpass
import time
import pdb
import configparser

ERROR = "\033[91m" + "[ERROR]" + "\033[0m"

def parse_config():
    config = configparser.ConfigParser()
    try:
        config.read('/etc/zypper-automatic.ini')
        email_to = config['EMAIL']['EMAIL_TO']
    except KeyError:
        sys.exit(f"{ERROR} Please check /etc/zypper-automatic.ini")
    return email_to

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
        output = subprocess.check_output(["zypper", "patch", "--category", "security", "--no-confirm", "--with-interactive", "--details"])
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
    command = subprocess.Popen(["mail", "-s", subject, email_to], stdin=message.stdout, stdout=subprocess.PIPE)
    message.stdout.close()
    output = command.communicate()[0]
    return output

def compose_body(time_start):
    ref_out = refresh_repos()
    ins_out = install_patches()
    lis_out = list_patches()
    
    outputs = {'ref_out': ref_out,
               'ins_out': ins_out,
               'lis_out': lis_out}
    
    # Convert bytes to strings if needed.
    for key, value in outputs.items():
        if type(value) is bytes:
            outputs[key] = str(value, 'utf-8')
    
    head = f"JOB STARTED: {time_start}"
    
    # Combine outputs to create body of message.
    body = "\n".join(outputs.values())
    
    return body

if __name__ == "__main__":
    time_start = time.asctime(time.localtime(time.time()))
    subject = "zypper-automatic"
    email_to = parse_config()
    
    check_root()
    body = compose_body(time_start)
    send_email(body, subject, email_to)
