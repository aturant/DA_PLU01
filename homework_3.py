from fastapi import APIRouter, Response, Request, HTTPException, Cookie
from fastapi.responses import HTMLResponse
from datetime import date, datetime

# security imports
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import json

router = APIRouter()

# security additions
security = HTTPBasic()
loginy={'4dm1n':'NotSoSecurePa$$'}
session_ids={"12334","4567"}

@router.get("/hello", response_class=HTMLResponse)
def hello():
	return_string="<h1>Hello! Today date is {}</h1>".format(date.today().strftime('%Y-%m-%d'))

	return return_string


######################################################################
@router.post("/login_token", status_code=201)
@router.post("/login_session", status_code=201)
def main(
	response: Response,
	request:Request,
	credentials: HTTPBasicCredentials = Depends(security),
	session_token: str = Cookie(None)
	):
	global session_ids
	print(session_ids)

	if session_token in session_ids:
		return {"token": session_token} 

	session_dict={}
	session_dict["username"]=credentials.username
	session_dict["password"]=credentials.password
	session_dict["url"]=str(request.url)



	if not session_dict["username"] in loginy.keys():
		raise HTTPException(status_code=401,detail="login not found")

	elif loginy[session_dict["username"]]!=session_dict["password"]:
		raise HTTPException(status_code=401,detail="wrong password")

	else:
		session_token=str(datetime.now()).replace(" ","")

		session_ids.add(session_token)
		
		response.set_cookie(
			key="session_token", 
			value=session_token)
		return {"token": session_token} 


###############################################################################
# Skoro mamy już utworzoną sesję, czas na jej użycie. Dla metody GET, stwórz endpointy /welcome_session oraz /welcome_token. Oba endpointy mają wpuścić tylko zalogowanych użytkowników. W sytuacji błędnego klucza sesji lub jego braku, należy zwrócić kod HTTP 401. Pierwszy endpoint otrzyma klucz sesji w utworzonym cookie. Drugi endpoint otrzyma klucz w adresie url, poprzez parametr token. 
#Po poprawnej walidacji klucza sesji, endpointy w zależności od otrzymanego (lub też nie) query parametru format w adresie url, mają zwrócić kod HTTP 200 oraz odpowiedną wiadomość z pasującym nagłówkiem content-type:
# - format=json - należy zwrócić następującą wiadomość w formacie json: {"message": "Welcome!"}
# - format=html - należy zwrócić dowolną wiadomość w formacie html, która ma zawierać następujący fragment: <h1>Welcome!</h1>
# - w pozostałych przypadkach należy zwrócić wiadomość Welcome! w formacie plain


@router.get("/welcome_session")

#/welcome_token?token=verylongvalueXOXOXOXOXO&format=json

@router.get("/welcome_token")
def main(
	format: str="plain", 	
	token: str=None,
	session_token: str = Cookie(None)):

	__mime_dict={
					"json":"application/json",
					"plain":"text/plain",
					"html":"text/html"}

	__token=token if token else session_token
	__format=format
	if __token not in session_ids:
		__format="plain"
		raise HTTPException(status_code=401,detail="wrong password")

	if __format not in __mime_dict.keys():
		raise HTTPException(status_code=401,detail="wrong format")

	if format=="json":
		message=json.dumps({"message":"Welcome!"})
			
	elif format=="html":
		message="<h1>Welcome!</h1>"
	
	else:
		message="Welcome!"

	print(message)
	return Response(
			media_type=str(__mime_dict[__format]),
			content=str(message),
			status_code=200)


# Skoro coś utworzono, można też to usunąć (tak jak ten opis pracy domowej za pierwszym podejściem - sic!). Dla metody DELETE stwórz najpierw dwa endpointy /logout_session oraz /logout_token. Tak jak w poprzednim zadaniu, należy wpuścić tylko użytkowników z ważnym kluczem sesji. Błędny klucz sesji lub jego brak oznacza zwrotkę kodu HTTP 401. Po poprawnej autentykacji, oba endpointy mają unieważnić klucz sesji poprzez wyczyszczenie pamięci podręcznej aplikacji. Następnie mają przekierować z kodem HTTP 302 (dopuszczalny jest też kod HTTP 303) do endpointu /logged_out, który również należy utworzyć.

# Endpoint /logged_out jest obsługiwany przez metodę GET i w zależności od przekazanego parametru format w adresie url, ma zwrócić kod HTTP 200 oraz odpowiednią wiadomość z odpowiadającym nagłówkiem content-type:

# format=json - należy zwrócić następującą wiadomość w formacie json: {"message": "Logged out!"}
# format=html - należy zwrócić dowolną wiadomość w formacie html, która ma zawierać następujący fragment: <h1>Logged out!</h1>
# w pozostałych przypadkach należy zwrócić wiadomość Logged out! w formacie plain
# Przykładowy request:

# /logout_token?token=verylongvalueXOXOXOXOXO&format=html