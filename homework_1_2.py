from fastapi import APIRouter, Request, Response
from hashlib import sha512
from datetime import timedelta, date
from typing import Optional

from pydantic import BaseModel



class InItem(BaseModel):
    id: Optional[int]
    name: str
    surname: str
    register_date: Optional[str] = None
    vaccination_date: Optional[str] = None
    
router_1 = APIRouter()
router_1.client_id = 0
router_1.patients=dict()


@router_1.get("/")
def root():
    return {"message": "Hello World!"}


@router_1.get("/method")
@router_1.put("/method")
@router_1.options("/method")
@router_1.delete("/method")
@router_1.post("/method", status_code=201)
def root(request: Request, response: Response):
    return {"method": request.method}


@router_1.get("/auth")
def root(
        response: Response,
        password: str,
        password_hash: str):
    try:
        if (len(password) + len(password_hash)) == 0:
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


@router_1.post('/register', status_code=201)
def root(in_item: InItem):
    # in_item.name=in_item.name.strip()
    # in_item.surname=in_item.surname.strip()

    router_1.client_id += 1
    in_item.id = router_1.client_id
    offset = len(in_item.name) + len(in_item.surname)
    vaccination_date = date.today() + timedelta(days=offset)

    in_item.register_date = date.today().strftime('%Y-%m-%d')
    in_item.vaccination_date = vaccination_date.strftime('%Y-%m-%d')

    router_1.patients[in_item.id] = in_item
    return in_item


@router_1.get('/patient/{id}')
def root(id: int, response: Response):
    if id < 1:
        response.status_code = 400

    elif id > router_1.client_id:
        response.status_code = 404

    else:
        return router_1.patients[id]

    return None