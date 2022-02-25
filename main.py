from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from api.db_connect import database

from api.placements.views import placement_router
from api.users.views import user_router
from api.streams.views import stream_router
app = FastAPI()

origins = ["http://localhost:3000", "localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    # from api.assist import drop_tables, insert_rows
    # drop_tables()
    # insert_rows()
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(placement_router)
app.include_router(user_router)
app.include_router(stream_router)
