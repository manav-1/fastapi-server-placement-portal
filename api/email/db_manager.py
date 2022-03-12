from api.db import EmailData, User
from .models import *
from api.db_connect import database


async def add_email_to_db(email_data: EmailDbIn):
    """
    Add Email Data to Database
    """
    query = EmailData.insert().values(**email_data.dict())
    await database.execute(query)


async def get_all_emails():
    """
    Get All Emails
    """
    query = EmailData.join(
        User, User.c.user_id == EmailData.c.email_sent_by_user_id, isouter=True).select()
    return await database.fetch_all(query)
