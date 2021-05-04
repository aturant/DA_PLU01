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
session_ids={}

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
	my_cookie: str = Cookie(None)
	):


	session_dict={}
	session_dict["username"]=credentials.username
	session_dict["password"]=credentials.password
	session_dict["url"]=str(request.url)

	if !my_cookie:
		pass
	elif my_cookie["session_token"] in session_ids:
		return 

	if not session_dict["username"] in loginy.keys():
		raise HTTPException(status_code=401,detail="login not found")

	elif loginy[session_dict["username"]]!=session_dict["password"]:
		raise HTTPException(status_code=401,detail="wrong password")

	
		# poprawne logowanie
	if "login_token" in session_dict:
		return {"token": my_cookie}

	if "login_session" in session_dict:
		session_token=1234
		session_ids.add(session_token)
		
		response.set_cookie(
			key="session_token", 
			value=session_token)
		return session_dict
