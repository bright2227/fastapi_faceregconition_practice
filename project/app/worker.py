import os
import time

from celery import Celery
from face_recognition import face_encodings
import numpy as np


os.environ["C_FORCE_ROOT"] = "1"
celery = Celery(__name__)

celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis+socket:///var/run/redis/redis-server.sock")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis+socket:///var/run/redis/redis-server.sock")
celery.conf.result_expires = 1
celery.conf.task_serializer = "pickle"
celery.conf.result_serializer = 'pickle'
celery.conf.accept_content = ['pickle']
celery.conf.result_accept_content = ['pickle']


@celery.task(name="face_recog_task")
def face_recog_task(image:np.array) -> np.array:
    [encode] = face_encodings(image)
    return encode

'''
celery --app=app.worker worker --detach
celery --app=app.worker control shutdown
'''