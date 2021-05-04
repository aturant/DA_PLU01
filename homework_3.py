from fastapi import APIRouter, Response, Request, HTTPException, Cookie
from fastapi.responses import HTMLResponse
from datetime import date

# security imports
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

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
		session_token=str(1234)
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


@router.get("/welcome_session", status_code=200)

#/welcome_token?token=verylongvalueXOXOXOXOXO&format=json

@router.get("/welcome_token", status_code=200)
def main(
	token: str=None,
	format: str="plain", 
	session_token: str = Cookie(None),
	response:Response ):

	__mime_dict={
					"json":"application/json",
					"plain":"text/plain",
					"html":"text/html"}

	__token=token if token else session_token
	__format=format
	if __token not in session_ids:
		raise HTTPException(status_code=401,detail="wrong password")

	if format=="json":
		message={"message": "Welcome!"}
	
	elif format=="html":
		message=="<h1>Welcome!</h1>"
	
	else:
		message="Welcome!"

	response.media_type=__mime_dict[__format]
	response.content=message
	return message