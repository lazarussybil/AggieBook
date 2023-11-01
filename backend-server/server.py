
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from socketserver import BaseServer
from dbOps import *
import os

CLIENT_ADDRESS = "../frontend-web/"

class AggieBookServer(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server: BaseServer) -> None:
        super().__init__(request, client_address, server)
        # self.conn = sqlite3.connect(DATABASE_PATH)
        # self.cursor = self.conn.cursor()

    def do_GET(self):
        if self.path in ('/', '/login'):
            self.serve_static_file('login.html')
        elif self.path in ('/register'):
            self.serve_static_file('register.html')
        elif self.path.endswith('.html') or self.path.endswith('.css') or self.path.endswith('.js') or self.path.endswith('.jpg'):
            self.serve_static_file(self.path)
        else:
            self.send_error(404, "File not found.")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_body = json.loads(post_data)
        print("====== Here comes to the post part: ", post_body)
        if self.path == '/register':
            # Handle user registration
            self.handle_register(post_body)
        elif self.path == '/newstory':
            # Handle new story submission
            self.handle_newstory(post_body)
        elif self.path == '/unfollow':
            self.handle_unfollow(post_body)
        elif self.path == '/follow':
            self.handle_follow(post_body)
        elif self.path == '/searchUser':
            self.handle_searchfriend(post_body)
        elif self.path == '/like':
            self.handle_toggle_like(post_body)
        elif self.path == '/comment':
            self.handle_comment(post_body)
        else:
            self.send_error(404, "Endpoint not found.")

    def do_PUT(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_body = json.loads(post_data)
        print("====== Here comes to the put part: ", post_body)
        if self.path == '/login':
            # Handle login
            self.handle_login(post_body)
        elif self.path == '/userinfo':
            self.handle_update_userinfo(post_body)
        elif self.path == '/follower':
            self.handle_get_followers(post_body)
        elif self.path == '/following':
            self.handle_get_following(post_body)
        else:
            self.send_error(404, "Endpoint not found.")
            

    def serve_static_file(self, filename):
        try:
            # Ensure that only intended files are accessible
            file_path = CLIENT_ADDRESS+filename
            print("file path is ", file_path)
            with open(file_path, 'rb') as f:
                self.send_response(200)
                if file_path.endswith('.html'):
                    self.send_header('Content-type', 'text/html')
                elif file_path.endswith('.css'):
                    self.send_header('Content-type', 'text/css')
                elif file_path.endswith('.js'):
                    self.send_header('Content-type', 'application/javascript')
                self.end_headers()
                self.wfile.write(f.read())
        except Exception as e:
            self.send_error(404, f"File not found: {e}")


    def handle_get_followers(self, data):
        userID = data['userID']

        followers = get_followers(userID)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = {
            'status': 'success',
            'message': 'Fetched followers successfully',
            'data': {
                'followers': followers,
            }
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def handle_get_following(self, data):
        userID = data['userID']

        following = get_following(userID)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = {
            'status': 'success',
            'message': 'Fetched following users successfully',
            'data': {
                'following': following,
            }
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))


    def handle_comment(self, post_body):
        userID = post_body['userID']
        postID = post_body['postID']
        content = post_body['content']
        comment(user_id=userID, post_id=postID, content=content)
        timeline = get_timeline_for_user(userID=userID)
        response = {
            'status': 'success',
            'message': 'comment successful',
            'data': {
                'timeline': timeline,
            },
        }
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        self.wfile.write(json.dumps(response).encode('utf-8'))


    def handle_toggle_like(self, post_body):
        userID = post_body['userID']
        postID = post_body['postID']
        
        toggle_like(user_id=userID, post_id=postID)

        timeline = get_timeline_for_user(userID=userID)
        response = {
            'status': 'success',
            'message': 'like toggle successful',
            'data': {
                'timeline': timeline,
            },
        }
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        self.wfile.write(json.dumps(response).encode('utf-8'))

        

    def handle_login(self, credentials):
        userID = get_userID(credentials['username'], credentials['password'])
        if userID:
            personal_info = get_personal_info(userID=userID)
            timeline = get_timeline_for_user(userID=userID)
            following_counts, followed_counts = get_follow_counts(userID=userID)
            response = {
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'userID': userID,
                    'personal_info' : personal_info,
                    'timeline': timeline,
                    'following_counts': following_counts,
                    'followed_counts': followed_counts,
                },
            }
        else:
            response = {
                'status': 'fail',
                'message': 'Invalid credentials'
            }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def handle_follow(self, post_body):
        userID = post_body['userID']
        targetUserID = post_body['targetUserID']
        follow_insert(userID=userID, targetUserID=targetUserID)
        following_counts, followed_counts = get_follow_counts(userID=userID)
        timeline = get_timeline_for_user(userID=userID)
        response = {
            'status': 'success',
            'message': 'follow successful',
            'data': {
                'following_counts': following_counts,
                'followed_counts': followed_counts,
                'timeline': timeline,
            }
        }
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        self.wfile.write(json.dumps(response).encode('utf-8'))


    def handle_unfollow(self, post_body):
        userID = post_body['userID']
        targetUserID = post_body['targetUserID']
        follow_delete(userID=userID, targetUserID=targetUserID)
        following_counts, followed_counts = get_follow_counts(userID=userID)
        timeline = get_timeline_for_user(userID=userID)
        response = {
            'status': 'success',
            'message': 'follow successful',
            'data': {
                'following_counts': following_counts,
                'followed_counts': followed_counts,
                'timeline': timeline,
            }
        }
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        self.wfile.write(json.dumps(response).encode('utf-8'))


    def handle_register(self, user_data):
        username = user_data['username']
        password = user_data['password']
        displayname = user_data['displayname']
        user_insert(username=username, password=password, displayname=displayname)
        response = {
            'status': 'success',
            'message': 'register successful',
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

        
    def handle_newstory(self, story_data):
        userID = story_data.get('userID')
        title = story_data.get('title')
        content = story_data.get('content')
        
        post_insert(userID, title, content)
        timeline = get_timeline_for_user(userID=userID)
        response = {
            'status': 'success',
            'message': 'newstory successful',
            'data': {
                'timeline': timeline,
            }
        }

        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def handle_update_userinfo(self, update_data):
        conn = get_db_connection()
        cursor = conn.cursor()

        attr = update_data["attr"]
        value = update_data["value"]
        userID = update_data["userID"]

        cursor.execute(f"UPDATE userinfo SET {attr} = ? WHERE userID = ?", (value, userID))
        conn.commit()

        personal_info = get_personal_info(userID=userID)
        response = {
            'status': 'success',
            'message': 'Login successful',
            'data': {
                'personal_info' : personal_info,
            }
        }
        conn.close()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        

    def handle_searchfriend(self, data):
        userID = data['userID']
        token = data['token']

        users = get_user_with_following_status(userID, token)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = {
            'status': 'success',
            'message': 'follow successful',
            'data': {
                'users': users,
            }
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
        


if __name__ == "__main__":
    httpd = HTTPServer(('localhost', 8000), AggieBookServer)
    httpd.serve_forever()