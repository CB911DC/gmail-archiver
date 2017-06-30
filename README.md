# gmail-archiver

Gmail archive tool that exports the inbox and sent items as an `.mbox` file, and then uploads it to S3.


## Installation

- [boto3](https://boto3.readthedocs.io/en/latest/)


### Requirements

To use this tool you'll need to install it's dependencies:

`pip install -r requirements.txt`


### Boto

As we are using `boto3`, we will need to setup auth credentials that have write access to S3 buckets. This can be done via `awscli`:

```
aws configure
```

Alternatively you can set configure this manually at `~/.aws/credentials`:

```
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

We will also need to set the default region at `~/.aws/config`:

```
[default]
region=eu-west-1
```


## Usage

```
python gmail_archiver.py
```

The script will prompt you for the `Username` and `Password` of the Gmail account, and then it will prompt for the name of the `S3 Bucket`.

The script will give you feedback as to what it's doing and whether it was successful.

If the mailbox is large, I would recommend running them in a [screen](https://www.gnu.org/software/screen/manual/screen.html) session.
