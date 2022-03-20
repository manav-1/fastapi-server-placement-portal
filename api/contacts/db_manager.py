from api.db import *
from api.db_connect import database
from .models import *


async def get_contacts():
    query = Contact.select()
    return await database.fetch_all(query)


async def get_contact(contact_id: int):
    query = Contact.select().where(Contact.c.contact_id == contact_id)
    return await database.fetch_one(query)


async def update_contact(contact_id: int, contact: ContactUpdate):
    query = Contact.update().where(Contact.c.contact_id == contact_id).values(
        **contact.dict(exclude_unset=True))
    return await database.execute(query)


async def delete_contact(contact_id: int):
    query = Contact.delete().where(Contact.c.contact_id == contact_id)
    return await database.execute(query)


async def create_contact(contact: ContactIn):
    query = Contact.insert().values(**contact.dict(exclude_unset=True))
    return await database.execute(query)


async def get_core_team_contacts():
    query = Contact.select().where(Contact.c.contact_position == ContactPosition.CORE)
    return await database.fetch_all(query)


async def get_secretaries_contacts():
    query = Contact.select().where(
        Contact.c.contact_position == ContactPosition.SECRETARY)
    return await database.fetch_all(query)
