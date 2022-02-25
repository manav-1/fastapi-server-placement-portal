import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv
from datetime import date
from botocore.client import Config
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

ACCESS_KEY = os.environ["AWS_AKEY"]
SECRET_KEY = os.environ["AWS_SKEY"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]
CONTEXT = ssl.create_default_context()


def upload_to_bucket(file,user_id, bucket='kmv-placements'):
    s3 = boto3.client(
        "s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY
    )
    try:
        date_today = date.today()
        path = f"resume/{file.filename}_{user_id}_{date_today.year}_{date_today.month}"
        s3.upload_fileobj(file.file, bucket, path)
        return path
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def get_file_from_bucket(bucket, file, path):
    session = boto3.Session(
        aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY
    )
    s3 = session.resource("s3")
    s3_bucket = s3.Bucket(bucket)
    try:
        res = s3_bucket.download_file(path, file)
        print("Download Successful", res)
        return res
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def upload_to_aws_file(file, bucket, company, po_id, type="poso"):
    s3 = boto3.client(
        "s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY
    )
    date_today = date.today()
    try:
        res = s3.upload_file(
            file,
            bucket,
            f"poso/{company}/{date_today.year}/{date_today.month}/{po_id}/{type}_attachments/{file}",
        )
        print("Upload Successful", res)
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def get_file_url_from_bucket(bucket, path, expiration=3600):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name='ap-south-1',
        config=Config(signature_version="s3v4"),
    )
    try:
        response = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": path},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        print(e)
        return None
    return response


def send_email(receiver_email, subject, message):
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls(context=CONTEXT)
    server.login(SMTP_USER, SMTP_PASSWORD)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = receiver_email
    msg.attach(MIMEText(message, "plain"))
    server.send_message(msg)