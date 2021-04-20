from fastapi import FastAPI, Request, Response

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World!"}


@app.get("/method")
@app.put("/method")
@app.options("/method")
@app.delete("/method")
@app.post("/method")
def root(request: Request, response: Response):
    if request.method in ['GET', 'PUT', 'OPTIONS', 'DELETE']:
        response.status_code = 200
        return {"method": request.method}

    elif request.method == 'POST':
        response.status_code = 201
        return {"method": request.method}
    
