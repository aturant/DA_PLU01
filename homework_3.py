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
session_ids=set()

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