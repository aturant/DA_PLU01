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
# Skoro mamy już utworzoną sesję, czas na jej użycie. Dla metody GET, stwórz endpointy /welcome_session oraz /welcome_token. Oba endpointy mają wpuścić tylko zalogowanych użytkowników. W sytuacji błędnego klucza sesji lub jego braku, należy zwrócić kod HTTP 401. Pierwszy endpoint otrzyma klucz sesji w utworzonym cookie. Drugi endpoint otrzyma klucz w adresie url, poprzez parametr token. 
# Po poprawnej walidacji klucza sesji, endpointy w zależności od otrzymanego (lub też nie) query parametru format w adresie url, mają zwrócić kod HTTP 200 oraz odpowiedną wiadomość z pasującym nagłówkiem content-type:
# - format=json - należy zwrócić następującą wiadomość w formacie json: {"message": "Welcome!"}
# - format=html - należy zwrócić dowolną wiadomość w formacie html, która ma zawierać następujący fragment: <h1>Welcome!</h1>
# - w pozostałych przypadkach należy zwrócić wiadomość Welcome! w formacie plain


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
# Skoro coś utworzono, można też to usunąć (tak jak ten opis pracy domowej za pierwszym podejściem - sic!). Dla metody DELETE stwórz najpierw dwa endpointy /logout_session oraz /logout_token. Tak jak w poprzednim zadaniu, należy wpuścić tylko użytkowników z ważnym kluczem sesji. Błędny klucz sesji lub jego brak oznacza zwrotkę kodu HTTP 401. Po poprawnej autentykacji, oba endpointy mają unieważnić klucz sesji poprzez wyczyszczenie pamięci podręcznej aplikacji. Następnie mają przekierować z kodem HTTP 302 (dopuszczalny jest też kod HTTP 303) do endpointu /logged_out, który również należy utworzyć.

# Endpoint /logged_out jest obsługiwany przez metodę GET i w zależności od przekazanego parametru format w adresie url, ma zwrócić kod HTTP 200 oraz odpowiednią wiadomość z odpowiadającym nagłówkiem content-type:

# format=json - należy zwrócić następującą wiadomość w formacie json: {"message": "Logged out!"}
# format=html - należy zwrócić dowolną wiadomość w formacie html, która ma zawierać następujący fragment: <h1>Logged out!</h1>
# w pozostałych przypadkach należy zwrócić wiadomość Logged out! w formacie plain
# Przykładowy request:

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
# Czas na grande finale! Dotychczas trzymaliśmy w pamięci podręcznej tylko jeden klucz sesji opartej o cookie i jeden opartej o tokeny, więc teraz to zmienimy. Wprowadź następujące zmiany:
# - dla endpointów /login_session oraz /login_token za każdym razem generuj unikalny klucz sesji, oraz w pamięci podręcznej zachowuj tylko ostatnie trzy utworzone klucze, odpowiednio dla sesji opartej o cookie jak i o tokeny
# - dla endpointów /welcome_session oraz /welcome_token aby autentykacja obsługiwała tylko klucze sesji trzymane w pamięci podręcznej
# - dla endpointów /logout_session oraz /logout_token, aby autentykacja obsługiwała tylko klucze sesji trzymane w pamięci podręcznej, oraz żeby endpointy "niszczyły" z pamięci podręcznej tylko aktualnie użytego klucza sesji
