#!/usr/bin/env python

from boto3.s3.transfer import S3Transfer
import boto3
import getpass
import os
import subprocess
import configparser
import sys
import threading


# Credentials required for getmail to grab emails from Gmail
print"Please enter the credentials for the mailbox you wish to archive"
username = raw_input("Username: ")
password = getpass.getpass("Password: ")

print"Please enter the S3 bucket you wish to upload the .mbox archive to"
bucket_name = raw_input("S3 Bucket name: ")

def archive_mailbox():
    # Variables
    base_dir = os.path.expanduser("~/getmail/")
    config_path = "{base}getmail_config".format(base=base_dir)
    global mbox
    mbox = "{0}{1}.mbox".format(base_dir, username)

    # Create config file for getmail
    config = configparser.ConfigParser()
    config['retriever'] = {'type': 'SimpleIMAPSSLRetriever',
                           'server': 'imap.gmail.com',
                           'mailboxes': '("Inbox", "[Gmail]/Sent Mail")',
                           'username': username,
                           'password': password}

    config['destination'] = {'type': 'Mboxrd',
                             'path': mbox}

    config['options'] = {'delete': 'true',
                         'message_log': '{0}getmail_log'.format(base_dir)}

    # Create getmail and it's required directories
    try:
        if not os.path.exists(base_dir):
            print "Creating the base dir for getmail '{0}'".format(base_dir)
            os.makedirs(base_dir, 0775)

            dirs = ["cur", "new", "tmp"]

            for entry in dirs:
                print "Creating the '{0}' dir for getmail '{1}'".format(
                    entry,
                    base_dir
                    )
                os.makedirs("{0}{1}".format(base_dir, entry), 0775)

        open(mbox, 'w').close()

        with open(config_path, 'w') as configfile:
            config.write(configfile)

        # Download emails from Gmail using getmail
        print "Downloading the mailbox for {0} to `{1}`".format(
            username,
            mbox
            )

        subprocess.call(["getmail", "--all",
                         "--getmaildir={base}".format(base=base_dir),
                         "--dont-delete",
                         "--rcfile={config}".format(config=config_path)
                         ])
        print "The gmail archive has been successful for {0} to '{1}'".format(
            username,
            mbox
            )
    except Exception as e:
        print(e)
    finally:
        # Remove config file as it contains sensitive information
        print "Removing '{0}' as it contains secrets".format(config_path)
        os.remove(config_path)


# Required for the progress bar when uploading to S3
class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()


def s3_upload():
    # Create an S3 client
    s3 = boto3.client('s3')
    transfer = S3Transfer(s3)

    key = "{0}/{0}.mbox".format(username)

    # Upload files to S3 bucket
    try:
        transfer.upload_file(
            mbox,
            bucket_name,
            key,
            callback=ProgressPercentage(mbox)
            )
        print "'{0}, has been successfully uploaded to '{1}'".format(
            mbox,
            bucket_name
            )
    except Exception as e:
        print(e)


def main():
    archive_mailbox()
    s3_upload()


if __name__ == "__main__":
    main()
