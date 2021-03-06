from fastapi import APIRouter, Response, Request, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse

from datetime import date, datetime
from typing import Optional
from collections import deque

# security imports
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import json

router_3 = APIRouter()

router_3.mime_dict = {
    "json": "application/json",
    "plain": "text/plain",
    "html": "text/html"}

# security additions
security = HTTPBasic()
loginy = {'4dm1n': 'NotSoSecurePa$$'}
session_ids = deque({"12334", "4567"},3)

@router_3.get("/hello", response_class=HTMLResponse)
def hello():
    return_string = "<h1>Hello! Today date is {}</h1>".format(date.today().strftime('%Y-%m-%d'))

    return return_string


######################################################################

@router_3.post("/login_token", status_code=201)
@router_3.post("/login_session", status_code=201)
def main(
        response: Response,
        request: Request,
        credentials: HTTPBasicCredentials = Depends(security),
        session_token: str = Cookie(None)
):
    global session_ids
    print(session_ids)

    if session_token in session_ids:
        return {"token": session_token}

    session_dict = {}
    session_dict["username"] = credentials.username
    session_dict["password"] = credentials.password
    session_dict["url"] = str(request.url)

    if not session_dict["username"] in loginy.keys():
        raise HTTPException(status_code=401, detail="login not found")

    elif loginy[session_dict["username"]] != session_dict["password"]:
        raise HTTPException(status_code=401, detail="wrong password")

    else:
        session_token = str(datetime.now()).replace(" ", "")
        session_ids.remove(session_token)
        session_ids.append(session_token)

        response.set_cookie(
            key="session_token",
            value=session_token)
        return {"token": session_token}

    ###############################################################################


# Zadanie 3.3
# Skoro mamy ju?? utworzon?? sesj??, czas na jej u??ycie. Dla metody GET, stw??rz endpointy /welcome_session oraz /welcome_token. Oba endpointy maj?? wpu??ci?? tylko zalogowanych u??ytkownik??w. W sytuacji b????dnego klucza sesji lub jego braku, nale??y zwr??ci?? kod HTTP 401. Pierwszy endpoint otrzyma klucz sesji w utworzonym cookie. Drugi endpoint otrzyma klucz w adresie url, poprzez parametr token. 
# Po poprawnej walidacji klucza sesji, endpointy w zale??no??ci od otrzymanego (lub te?? nie) query parametru format w adresie url, maj?? zwr??ci?? kod HTTP 200 oraz odpowiedn?? wiadomo???? z pasuj??cym nag????wkiem content-type:
# - format=json - nale??y zwr??ci?? nast??puj??c?? wiadomo???? w formacie json: {"message": "Welcome!"}
# - format=html - nale??y zwr??ci?? dowoln?? wiadomo???? w formacie html, kt??ra ma zawiera?? nast??puj??cy fragment: <h1>Welcome!</h1>
# - w pozosta??ych przypadkach nale??y zwr??ci?? wiadomo???? Welcome! w formacie plain


@router_3.get("/welcome_session")
# /welcome_token?token=verylongvalueXOXOXOXOXO&format=json
@router_3.get("/welcome_token")
def main(
        format: Optional[str] = None,
        token: Optional[str] = None,
        session_token: Optional[str] = Cookie(None)):
    msg_dict = {
        "json": json.dumps({"message": "Welcome!"}),
        "plain": "Welcome!",
        "html": "<h1>Welcome!</h1>"}

    session_token = token if token else session_token

    print("session_token={}, token={}".format(session_token, token))

    if session_token not in session_ids:
        raise HTTPException(status_code=401,
                            detail="wrong password {}".format(session_token))

    format = format if format in router_3.mime_dict.keys() else "plain"

    return Response(
        media_type=str(router_3.mime_dictmime_dict[format]),
        content=msg_dict[format],
        status_code=200)


# Zadanie 3.4
# Skoro co?? utworzono, mo??na te?? to usun???? (tak jak ten opis pracy domowej za pierwszym podej??ciem - sic!). Dla metody DELETE stw??rz najpierw dwa endpointy /logout_session oraz /logout_token. Tak jak w poprzednim zadaniu, nale??y wpu??ci?? tylko u??ytkownik??w z wa??nym kluczem sesji. B????dny klucz sesji lub jego brak oznacza zwrotk?? kodu HTTP 401. Po poprawnej autentykacji, oba endpointy maj?? uniewa??ni?? klucz sesji poprzez wyczyszczenie pami??ci podr??cznej aplikacji. Nast??pnie maj?? przekierowa?? z kodem HTTP 302 (dopuszczalny jest te?? kod HTTP 303) do endpointu /logged_out, kt??ry r??wnie?? nale??y utworzy??.

# Endpoint /logged_out jest obs??ugiwany przez metod?? GET i w zale??no??ci od przekazanego parametru format w adresie url, ma zwr??ci?? kod HTTP 200 oraz odpowiedni?? wiadomo???? z odpowiadaj??cym nag????wkiem content-type:

# format=json - nale??y zwr??ci?? nast??puj??c?? wiadomo???? w formacie json: {"message": "Logged out!"}
# format=html - nale??y zwr??ci?? dowoln?? wiadomo???? w formacie html, kt??ra ma zawiera?? nast??puj??cy fragment: <h1>Logged out!</h1>
# w pozosta??ych przypadkach nale??y zwr??ci?? wiadomo???? Logged out! w formacie plain
# Przyk??adowy request:

# /logout_token?token=verylongvalueXOXOXOXOXO&format=html

@router_3.delete('/logout_session')
@router_3.delete('/logout_token')
def main(
        format: Optional[str] = None,
        token: Optional[str] = None,
        session_token: Optional[str] = Cookie(None)):
    session_token = token if token else session_token
    print("session_token={}, token={}".format(session_token, token))

    if session_token not in session_ids:
        raise HTTPException(status_code=401,
                            detail="wrong token {}".format(session_token))
    session_ids.remove(session_token)
    return RedirectResponse(url=f'/logged_out?format={format}', status_code=303)


@router_3.get('/logged_out', status_code=200)
def main(format: Optional[str] = "plain"):
    msg_dict = {
        "json": json.dumps({"message": "Logged out!"}),
        "html": "<h1>Logged out!</h1>",
        "plain": "Logged out!"}
    if not (format in msg_dict.keys()):
        format = "plain"

    return Response(
        media_type=str(router_3.mime_dict[format]),
        content=msg_dict[format],
        status_code=200)

# 35
# Czas na grande finale! Dotychczas trzymali??my w pami??ci podr??cznej tylko jeden klucz sesji opartej o cookie i jeden opartej o tokeny, wi??c teraz to zmienimy. Wprowad?? nast??puj??ce zmiany:
# - dla endpoint??w /login_session oraz /login_token za ka??dym razem generuj unikalny klucz sesji, oraz w pami??ci podr??cznej zachowuj tylko ostatnie trzy utworzone klucze, odpowiednio dla sesji opartej o cookie jak i o tokeny
# - dla endpoint??w /welcome_session oraz /welcome_token aby autentykacja obs??ugiwa??a tylko klucze sesji trzymane w pami??ci podr??cznej
# - dla endpoint??w /logout_session oraz /logout_token, aby autentykacja obs??ugiwa??a tylko klucze sesji trzymane w pami??ci podr??cznej, oraz ??eby endpointy "niszczy??y" z pami??ci podr??cznej tylko aktualnie u??ytego klucza sesji
