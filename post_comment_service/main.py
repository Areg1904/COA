import os
import uuid
import grpc
import psycopg2
from concurrent import futures
from datetime import datetime, timezone

import posts_pb2, posts_pb2_grpc
from google.protobuf.empty_pb2 import Empty

GRPC_PORT = os.getenv("GRPC_PORT", 8002)

class PostsService(posts_pb2_grpc.PostsServiceServicer):
    def __init__(self):
        self.connection = psycopg2.connect(
            host='db-post-comment-service',
            database='posts',
            user='user',
            password='password'
        )
        self.create_table()

    def create_table(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id UUID PRIMARY KEY,
                user_id TEXT,
                title TEXT,
                description TEXT,
                privacy_flag BOOLEAN,
                tags TEXT[],
                created_at TIMESTAMP WITH TIME ZONE,
                updated_at TIMESTAMP WITH TIME ZONE
            );
            """)
            self.connection.commit()

    def CreatePost(self, request, context):
        post_id = uuid.uuid4()
        created_at = datetime.now(timezone.utc)
        updated_at = created_at
        tags = "{" + ",".join(request.post.tags) + "}"

        with self.connection.cursor() as cursor:
            cursor.execute("""
            INSERT INTO posts (post_id, user_id, title, description, privacy_flag, tags, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (str(post_id), request.post.user_id, request.post.title, request.post.description, request.post.privacy_flag, tags, created_at, updated_at))
            self.connection.commit()
        
        return posts_pb2.CreatePostResponce(post_id=str(post_id))

    def DeletePost(self, request, context):
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM posts WHERE post_id = %s", (request.post_id,))
            self.connection.commit()
        return Empty()

    def UpdatePost(self, request, context):
        updated_at = datetime.now(timezone.utc)
        tags = "{" + ",".join(request.post.tags) + "}"

        with self.connection.cursor() as cursor:
            cursor.execute("""
            UPDATE posts SET user_id = %s, title = %s, description = %s, privacy_flag = %s, tags = %s, updated_at = %s
            WHERE post_id = %s
            """, (request.post.user_id, request.post.title, request.post.description, request.post.privacy_flag, tags, updated_at, request.post.post_id))
            self.connection.commit()
        return Empty()

    def GetPost(self, request, context):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM posts WHERE post_id = %s", (request.post_id,))
            row = cursor.fetchone()
            if row:
                post = posts_pb2.Post(
                    post_id=row[0],
                    user_id=row[1],
                    title=row[2],
                    description=row[3],
                    privacy_flag=row[4],
                    tags=row[5],
                    created_at=row[6],
                    updated_at=row[7]
                )
                return posts_pb2.GetPostResponce(post=post)
        return posts_pb2.GetPostResponce()

    def GetPosts(self, request, context):
        offset = (request.page_number - 1) * request.page_size
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM posts WHERE privacy_flag = %s OFFSET %s LIMIT %s", (False, offset, request.page_size))
            rows = cursor.fetchall()
            posts = []
            for row in rows:
                post = posts_pb2.Post(
                    post_id=row[0],
                    user_id=row[1],
                    title=row[2],
                    description=row[3],
                    privacy_flag=row[4],
                    tags=row[5],
                    created_at=row[6],
                    updated_at=row[7]
                )
                posts.append(post)
            return posts_pb2.GetPostsResponce(posts=posts)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    posts_pb2_grpc.add_PostsServiceServicer_to_server(PostsService(), server)
    server.add_insecure_port(f'[::]:{GRPC_PORT}')
    server.start()
    print(f"Server started on port {GRPC_PORT}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
