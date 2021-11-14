import asyncio
import time
from pathlib import Path
from shutil import copyfileobj
from typing import Any, List

import numpy as np
from app.db import get_session
from app.models import Picture, PictureBase, User, UserBase
from app.worker import face_recog_task
from face_recognition import compare_faces, load_image_file
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter(prefix="/user",)

FOLDER_BASE_ADDR = Path(__file__).resolve().parent.parent


@router.get("/",response_model=List[User])
async def get_user(session:AsyncSession=Depends(get_session)):
    result = await session.execute(select(User.name))
    users = result.scalars().all()
    return [user.name for user in users]


@router.get("/picture/",response_model=List[PictureBase])
async def get_pic(session:AsyncSession=Depends(get_session)):
    result = await session.execute(select(Picture))
    pictures = result.scalars().all()
    return list(pictures)


@router.post("/", response_model=User)
async def create_user(user:UserBase, session:AsyncSession=Depends(get_session)):
    user = User.from_orm(user)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/{user_id}/picture/", response_model=int)
async def upload_pic(user_id:int, upload_file:UploadFile=File(...), session:AsyncSession=Depends(get_session)):
    stat = select(func.count(Picture.id)).where(Picture.user_id==user_id)
    res = await session.execute(stat)
    num = res.scalars().one()

    file_addr = f"{FOLDER_BASE_ADDR}/pics/{user_id}_{num}.png"
    with open(file_addr, "wb") as buffer:
        copyfileobj(upload_file.file, buffer)

    upload_file.file.seek(0)
    image = load_image_file(upload_file.file)
    task = face_recog_task.apply_async(args=[image])
    image_encode = await await_result(task)

    pic = Picture(user_id=user_id, encode=image_encode.tolist(), pic_addr=file_addr)
    session.add(pic)
    await session.commit()
    await session.refresh(pic)
    return pic.id


@router.get("/{user_id}/verification/", response_model=bool)
async def verify_pic(user_id:int, upload_file:UploadFile=File(...), session:AsyncSession=Depends(get_session)):
    stat = select(Picture.encode).where(Picture.user_id==user_id)
    result = await session.execute(stat)
    encodes = result.scalars().all()

    if not encodes:
        return False

    encodes = np.array(encodes)

    test_image = load_image_file(upload_file.file)
    task = face_recog_task.apply_async(args=[test_image])
    test_image_encode = await await_result(task)

    [is_same] = compare_faces(encodes, test_image_encode)
    return bool(is_same)


async def await_result(task, wait_sec:float=0.15, wait_limit:float=10) -> Any:
    st = time.time()
    while task.result is None:
        await asyncio.sleep(wait_sec)

        if time.time()-st > wait_limit:
            raise asyncio.TimeoutError(f'Model Task Timout for {wait_limit}')

    return task.result
