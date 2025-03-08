from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

async def proxy_request(method: str, path: str, request: Request):
    async with httpx.AsyncClient() as client:
        url = f"{USER_SERVICE_URL}{path}"
        headers = request.headers
        body = await request.body()
        
        try:
            response = await client.request(method, url, headers=headers, data=body)
            return Response(content=response.content, status_code=response.status_code, headers=response.headers)
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request failed: {e}")

@app.post("/register")
async def register(request: Request):
    return await proxy_request("POST", "/register", request)

@app.post("/login")
async def login(request: Request):
    return await proxy_request("POST", "/login", request)

@app.get("/profile")
async def get_profile(request: Request):
    return await proxy_request("GET", f"/profile", request)

@app.put("/update-profile")
async def update_profile(request: Request):
    return await proxy_request("PUT", "/update-profile", request)
