from fastapi import FastAPI, Request, Response
from hashlib import sha512

app = FastAPI()


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
def root(response: Response,
	password: str,
	password_hash:str):
	
	try:

		m = sha512()
		m.update(password.encode('utf-8'))
		password_test_hash=str(m.hexdigest()).encode('utf-8')

		if password_test_hash in str(password_hash).encode('utf-8'):
			response.status_code=204
		else:
			response.status_code=401

	except NameError:
		response.status_code=667
	return {
			"password": password, 
			"password_hash":password_hash, 
			"new_hash":password_test_hash}