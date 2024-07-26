
from celery import Celery
from time import sleep

from fastapi import FastAPI
from celery.result import AsyncResult

#connect to local rabbitmq and db sqlite backend
app = Celery('tasks', broker = 'amqp://localhost', backend = 'db+sqlite:///db.sqlite3')

@app.task #register task into celery app via decorator
def get_hello(name):
    sleep(10) #simulation for long running task
    retval = f"Hello {name}"
    return retval


# Create FastAPI app instance
api = FastAPI()

# Endpoint to trigger the Celery task
@api.post("/say-hello/{name}")
async def say_hello(name: str):
    task = get_hello.delay(name)
    return {"task_id": task.id}

# Endpoint to get the result of a specific task
@api.get("/get-result/{task_id}")
async def get_result(task_id: str):
    task_result = AsyncResult(task_id, app=app)
    if task_result.ready():
        return {"status": "completed", "result": task_result.get()}
    return {"status": "pending"}
