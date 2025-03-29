from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import grpc
import os

import posts_pb2, posts_pb2_grpc

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")
GRPC_POST_COMMENT_URL = os.getenv("GRPC_POST_COMMENT_URL", "post-comment-service:8002")

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

@app.put("/create-post")
async def update_profile(request: Request):
    response: Response = await proxy_request("GET", "/verify-jwt", request)
    if response.status_code != 200:
        return response
    
    request_json = await request.json()

    post = posts_pb2.Post(
        user_id=json.loads(response.body)["user_id"],
        title=request_json.get("title", ""),
        description=request_json.get("description", ""),
        privacy_flag=request_json.get("privacy_flag", False),
        tags=request_json.get("tags", [])
    )

    with grpc.insecure_channel(GRPC_POST_COMMENT_URL) as channel:
        stub = posts_pb2_grpc.PostsServiceStub(channel)
        response = stub.CreatePost(posts_pb2.CreatePostRequest(post=post))

    return {"post_id": response.post_id}

@app.delete("/delete-post/{post_id}")
async def delete_post(request: Request, post_id: str):
    response: Response = await proxy_request("GET", "/verify-jwt", request)
    if response.status_code != 200:
        return response

    with grpc.insecure_channel(GRPC_POST_COMMENT_URL) as channel:
        stub = posts_pb2_grpc.PostsServiceStub(channel)
        response = stub.DeletePost(posts_pb2.DeletePostRequest(post_id=post_id))

    return {"message": "Post deleted successfully"}

@app.put("/update-post/{post_id}")
async def update_post(request: Request, post_id: str):
    response: Response = await proxy_request("GET", "/verify-jwt", request)
    if response.status_code != 200:
        return response

    request_json = await request.json()

    post = posts_pb2.Post(
        post_id=post_id,
        user_id=json.loads(response.body)["user_id"],
        title=request_json.get("title", ""),
        description=request_json.get("description", ""),
        privacy_flag=request_json.get("privacy_flag", False),
        tags=request_json.get("tags", [])
    )

    with grpc.insecure_channel(GRPC_POST_COMMENT_URL) as channel:
        stub = posts_pb2_grpc.PostsServiceStub(channel)
        response = stub.UpdatePost(posts_pb2.UpdatePostRequest(post=post))

    return {"message": "Post updated successfully"}

@app.get("/get-post/{post_id}")
async def get_post(request: Request, post_id: str):
    response: Response = await proxy_request("GET", "/verify-jwt", request)
    if response.status_code != 200:
        return response

    with grpc.insecure_channel(GRPC_POST_COMMENT_URL) as channel:
        stub = posts_pb2_grpc.PostsServiceStub(channel)
        response = stub.GetPost(posts_pb2.GetPostRequest(post_id=post_id))

    return {
        "post_id": response.post.post_id,
        "user_id": response.post.user_id,
        "title": response.post.title,
        "description": response.post.description,
        "privacy_flag": response.post.privacy_flag,
        "tags": list(response.post.tags),
        "created_at": str(response.post.created_at),
        "updated_at": str(response.post.updated_at)
    }

@app.get("/get-posts")
async def get_posts(request: Request):
    response: Response = await proxy_request("GET", "/verify-jwt", request)
    if response.status_code != 200:
        return response
    
    page_number = int(request.query_params.get("page_number", 1))
    page_size = int(request.query_params.get("page_size", 10))

    with grpc.insecure_channel(GRPC_POST_COMMENT_URL) as channel:
        stub = posts_pb2_grpc.PostsServiceStub(channel)
        response = stub.GetPosts(posts_pb2.GetPostsRequest(page_number=page_number, page_size=page_size))

    posts = []
    for post in response.posts:
        posts.append({
            "post_id": post.post_id,
            "user_id": post.user_id,
            "title": post.title,
            "description": post.description,
            "privacy_flag": post.privacy_flag,
            "tags": list(post.tags),
            "created_at": str(post.created_at),
            "updated_at": str(post.updated_at)
        })
    
    return {"posts": posts}