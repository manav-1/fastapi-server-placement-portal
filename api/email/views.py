from fastapi import APIRouter, status, UploadFile, HTTPException, Depends

from .models import *
import os
import ssl
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import shutil
import mimetypes
from api.db_connect import database
from api.users.models import UserOut
from api.users.views import get_current_active_user
from api.users.models import *

from .db_manager import add_email_to_db, get_all_emails

load_dotenv()
email_router = APIRouter(prefix="/email", tags=["Email"])

PLACEMENT_STYLE_TAGS = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Karla&display=swap");
.container {
width: 50%;
}
.fluid {
width: 100%;
}
.content {
display: flex;
}
.left-content {
width:25%
}
.right-content {
width: 75%
}
.h5 {
font-size: 0.9vw;
font-weight: 500;
font-family: karla;
text-align: justify ;
}

@media (max-width: 576px) {
.container {
    width: 100%;
}
.h5 {
    font-size: 2.2vw;
    font-weight: 500;
    font-family: karla;
    text-align: justify ;
}
}

</style>
"""
PLACEMENT_BODY_CONTENT = """
<body>
        <link href="https://fonts.googleapis.com/css2?family=Karla&display=swap" rel="stylesheet" type="text/css"/> 
        <div class='container'>
        <div class="header">
            <img class='fluid' src="https://i.ibb.co/mh4LCr2/Mailing-Content-Header.png" alt="Header.png">
        </div>
        <div class='content'>
            <div class='left-content'>
                <img class='fluid' src="https://i.ibb.co/nn7M39q/Left-Content.png" alt="Left Content">
            </div>
            <div class="right-content">
                <p class="h5">Dear Manager,<br>

                    Greetings from <b>Start@KMV, The Placement Cell Of Keshav Mahavidyalaya</b>, University of
                    Delhi.<br><br>

                    Keshav Mahavidyalaya, is regarded as one of the best off-campus colleges and has carved a niche
                    for
                    itself by garnering University positions year after year. The students of Keshav Mahavidyalaya
                    are a
                    diverse group of exceptional individuals, and have been placed in prestigious companies like<b>
                    Kearney, S&P Global, D.E.Shaw, EY, TresVista, Deloitte, ZS, Infosys & Gartner </b>, among
                    others.<br><br>

                    We wish to set new records this season, and thus, <b>invite your esteemed organization for campus
                    recruitments for the Batch of 2021-22.</b> We are open to On-campus, Off-campus and Virtual drives
                    as
                    well.<br><br>

                    PFA: Placement Brochure<br><br>

                    For further information, kindly contact -<br>
                    Aarushi: +91 9810443298<br>
                    Raghav: +91 8506036566<br><br>

                    Warm Regards<br>
                    Start@KMV<br>
                    The Placement Cell<br>
                    Keshav Mahavidyalaya<br>
                    University of Delhi<br>
                </p>
                <img class='fluid' src="https://i.ibb.co/1dbZp3K/Past-recruiters-mailing-content.png" alt="Past Recruiters">
            </div>
        </div>
    </div>

    </body>
"""
PLACEMENT_HTML_CONTENT = f"""
    <!DOCTYPE html>
        <html lang="en">
            <head>
                {PLACEMENT_STYLE_TAGS}
                <meta charset="UTF-8">
                <!-- <link rel="stylesheet" href="css/bootstrap.css"> -->
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Document</title>
            </head>
            {PLACEMENT_BODY_CONTENT}
        </html>
"""

INTERNSHIP_HTML_CONTENT = f"""Hello"""

FILE_PATH = 'files/Placement_Brochure.pdf'


@email_router.post('/', status_code=status.HTTP_201_CREATED)
@database.transaction()
async def send_email(payload: Email, current_user: UserOut = Depends(get_current_active_user)):
    """
    Send an email
    """
    try:
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        SMTP_USER = os.environ["SMTP_USER"]
        SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]
        if payload.sender_email and payload.password:
            SMTP_USER = payload.sender_email
            SMTP_PASSWORD = payload.password
        CONTEXT = ssl.create_default_context()
        # creating the server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls(context=CONTEXT)
        server.login(SMTP_USER, SMTP_PASSWORD)
        ctype, encoding = mimetypes.guess_type(FILE_PATH)
        maintype, subtype = ctype.split('/', 1)
        pdf = MIMEApplication(open(FILE_PATH, 'rb').read())
        pdf.add_header('Content-Disposition', 'attachment', filename=os.path.splitext(
            FILE_PATH)[0].split("/")[-1] + os.path.splitext(FILE_PATH)[1])

        import pandas as pd
        database = pd.read_csv(payload.sheet_url)
        database = database.iloc[payload.starting_number -
                                 1:payload.ending_number, ::]
        database[database.columns[0]] = database[database.columns[0]].fillna(
            "Hiring Manager").apply(
            lambda x: x.strip())
        database[database.columns[1]] = database[database.columns[1]].apply(
            lambda x: x.strip() if not x.isascii() else x)
        database.dropna(inplace=True)
        for email, name in zip(database[database.columns[1]], database[database.columns[0]]):
            # creating the msg content
            msg_content = PLACEMENT_HTML_CONTENT if payload.email_type else INTERNSHIP_HTML_CONTENT
            msg_content = msg_content.replace("Manager", name, 1)
            html_part = MIMEText(msg_content, 'html')
            # creating the msg Object
            msg = MIMEMultipart('alternative')
            msg['Subject'] = payload.subject
            msg['From'] = str(SMTP_USER)
            msg['To'] = str(email)
            msg.attach(html_part)
            msg.attach(pdf)
            server.send_message(msg)
            await add_email_to_db(EmailDbIn(hr_email=email, hr_name=name,
                                            email_sent_at=datetime.now(), email_sent_by_user_id=current_user.user_id, email_type=payload.email_type))
        server.quit()
        return {"message": "Email sent successfully",
                "status": status.HTTP_200_OK,
                "emails": list(database[database.columns[1]])}
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Invalid credentials for {SMTP_USER}")
    except smtplib.SMTPException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error in sending email: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error in sending email: {e}")


@email_router.post('/placement_brochure', status_code=status.HTTP_201_CREATED)
async def store_placement_brochure(file: UploadFile, current_user: UserOut = Depends(get_current_active_user)):
    """
    Store the Placement Brochure
    """
    if current_user.user_role == UserRole.ADMIN:
        try:
            file_location = f"files/Placement_Brochure.pdf"
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return {"info": f"file '{file.filename}' saved at '{file_location}'", "status": status.HTTP_201_CREATED}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
                                "message": f"Error in saving file: {e}"})
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={
                            "message": "Only admins can upload files"})


@email_router.get('/sent', status_code=status.HTTP_200_OK, response_model=List[EmailDbOut])
async def get_email_data(current_user: UserOut = Depends(get_current_active_user)):
    """
    Get the Email Data
    """
    if current_user.user_role == UserRole.ADMIN:
        return await get_all_emails()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={
                            "message": "You are not authorized to access this resource"})
