from fastapi import FastAPI

from homework_1_2 import router_1
from homework_3 import router_3
from homework_4 import router_4
from homework_5 import router as router_5

app = FastAPI()

app.include_router(router_5, tags=["homework5"])
app.include_router(router_1, tags=["homework1_2"])
app.include_router(router_3, tags=["homework3"])
app.include_router(router_4, tags=["homework4"])
