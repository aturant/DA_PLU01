from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from datetime import date

router = APIRouter()



@router.get("/hello", response_class=HTMLResponse)
def hello():

	return_string="<h1>Hello! Today date is {}</h1>".format(date.today().strftime('%Y-%m-%d'))

	return return_string