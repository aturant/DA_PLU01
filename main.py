from fastapi import FastAPI, Request, Response
from hashlib import sha512
from datetime import timedelta, date

from typing import Optional
from pydantic import BaseModel
import json

from pydantic import BaseModel


class InItem(BaseModel):
    id: Optional[int]
    name: str
    surname: str
    register_date: Optional[str] = None
    vaccination_date: Optional[str] = None


app = FastAPI()
app.client_id = 0
app.patients=dict()


@app.get("/")
def root():
    return {"message": "Hello World!"}


@app.get("/method")
@app.put("/method")
@app.options("/method")
@app.delete("/method")
@app.post("/method", status_code=201)
def root(request: Request, response: Response):
    return {"method": request.method}


@app.get("/auth")
def root(
	response: Response,
	password: str,
	password_hash: str):
	
	try:
		if (len(password)+len(password_hash))==0:
			raise KeyError

		m = sha512()
		m.update(password.encode('utf-8'))
		password_test_hash = str(m.hexdigest()).encode('utf-8')

		if (password_test_hash != str(password_hash).encode('utf-8')):
			raise KeyError

	except:
		response.status_code = 401

	else:
		response.status_code = 204
	
	finally:
		return None

@app.post('/register', status_code = 201)
def root(in_item: InItem):
	in_item.name=in_item.name.strip()
	in_item.surname=in_item.surname.strip()

	app.client_id += 1
	in_item.id = app.client_id
	offset = len(in_item.name) + len(in_item.surname) +1
	vaccination_date=date.today() + timedelta(days=offset)


	in_item.register_date = date.today().strftime('%Y-%m-%d')
	in_item.vaccination_date = vaccination_date.strftime('%Y-%m-%d')

	app.patients[in_item.id]=in_item
	return in_item

@app.get('/patient/{id}')
def root(id: int, response: Response):
	if id<1:
		response.status_code=400

	elif id>app.client_id:
		response.status_code=404

	else:
		return app.patients[id]
	
	return None