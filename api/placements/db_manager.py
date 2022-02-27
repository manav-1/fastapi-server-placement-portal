from sqlalchemy import and_
from fastapi import HTTPException
from .models import *
from api.db import *
from api.db_connect import database
import api.users.db_manager as user_manager
from fastapi import status


async def get_placements():
    query = Placements.select().where(Placements.c.is_active == True)
    return await database.fetch_all(query)


async def get_placement(placement_id: int):
    query = Placements.select().where(and_(Placements.c.placement_id ==
                                           placement_id, Placement.c.is_active == True))
    return await database.fetch_one(query)


async def get_placements_acc_to_user(user):
    user_profile = await user_manager.get_user_profile_by_user_id(user.user_id)
    if user_profile is not None:

        placements = await get_placements()
        applied_placements = await get_placements_by_user(user.user_id)
        return [placement for placement in placements if ((placement['placement_id'] not in [placements['placement_id'] for placements in applied_placements]) and (user_profile.stream_id in placement.stream_ids))]
        # return [placement for placement in placements if user_profile.stream_id in placement.stream_ids]
    else:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail="User profile not found")


async def create_placement(placement: Placement):
    query = Placements.insert().values(**placement.dict())
    return await database.execute(query)


async def update_placement(placement_id: int, placement: PlacementUpdate):
    query = Placements.update().values(
        **placement.dict(exclude_unset=True)).where(Placements.c.placement_id == placement_id)
    return await database.execute(query)


async def delete_placement(placement_id: int):
    query = Placements.update().values(is_active=False).where(
        Placements.c.placement_id == placement_id)
    return await database.execute(query)


async def get_placements_by_stream(stream_id: int):
    placements = await get_placements()
    return [placement for placement in placements if stream_id in placement.stream_ids]


async def get_placements_by_user(user_id: int):
    query = Placements.join(
        PlacementUserLinking, Placements.c.placement_id ==
        PlacementUserLinking.c.placement_id, isouter=True).\
        select().where(PlacementUserLinking.c.user_id == user_id)
    return await database.fetch_all(query)


async def get_applicants(placement_id: int):
    query = Placements.join(PlacementUserLinking, Placements.c.placement_id == PlacementUserLinking.c.placement_id, isouter=True).\
        join(User,  User.c.user_id == PlacementUserLinking.c.user_id).\
        select().where(PlacementUserLinking.c.placement_id == placement_id)
    data = await database.fetch_all(query)
    print(data, len(data))
    if len(data) != 0 or data != []:
        data_n = [dict(i) for i in data]
        import pandas as pd
        df = pd.DataFrame(data_n)
        df.drop(['user_password', 'user_role',  'user_created_at',
                'user_updated_at'], axis=1, inplace=True)
        # print(df)
        return df.to_csv()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No applicants found")


async def apply_placement(placement_id: int, user_id: int):
    query = PlacementUserLinking.select().where(PlacementUserLinking.c.placement_id ==
                                                placement_id, PlacementUserLinking.c.user_id == user_id)
    data = await database.fetch_one(query)
    if data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Already applied")
    else:
        query = PlacementUserLinking.insert().values(
            placement_id=placement_id, user_id=user_id)
        return await database.execute(query)
