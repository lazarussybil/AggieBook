
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from socketserver import BaseServer
from dbOps import *
import os
import requests


class AggieBookUserServer(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server: BaseServer) -> None:
        super().__init__(request, client_address, server)
        

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_body = json.loads(post_data)

        print(f"content_length {content_length}")
        print(f"post_data {post_data}")
        print(f"post_body {post_body}")

        if self.path == '/users/register':
            # Handle user registration
            self.handle_register(post_body)
        elif self.path == '/users/unfollow':
            self.handle_unfollow(post_body)
        elif self.path == '/users/follow':
            self.handle_follow(post_body)
        elif self.path == '/users/searchUser':
            self.handle_searchfriend(post_body)
        else:
            self.send_error(404, "Endpoint not found.")

    def do_PUT(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_body = json.loads(post_data)


        print(f"content_length {content_length}")
        print(f"post_data {post_data}")
        print(f"post_body {post_body}")
        
        if self.path == '/users/login':
            # Handle login
            self.handle_login(post_body)
        elif self.path == '/users/userinfo':
            self.handle_update_userinfo(post_body)
        elif self.path == '/users/follower':
            self.handle_get_followers(post_body)
        elif self.path == '/users/following':
            self.handle_get_following(post_body)
        else:
            self.send_error(404, "Endpoint not found.")
            

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
        

    def handle_login(self, credentials):
        userID = get_userID(credentials['username'], credentials['password'])
        if userID:
            personal_info = get_personal_info(userID)
            timeline = get_timeline_for_user(userID)
            following_counts, followed_counts = get_follow_counts(userID)
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
        print(f"post_body {post_body}")
        userID = post_body['userID']
        targetUserID = post_body['target_user_id']
        follow_insert(userID=userID, target_user_id=targetUserID)
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
        targetUserID = post_body['target_user_id']
        follow_delete(userID=userID, target_user_id=targetUserID)
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

        

    def handle_update_userinfo(self, update_data):
        mongo_conn = get_mongodb_connection()
        db = mongo_conn.AggieBook
        users_collection = db.userinfo

        attr = update_data["attr"]
        value = update_data["value"]
        user_id = update_data["userID"]

        # MongoDB uses '$set' operator for updating a specific field
        from bson import ObjectId
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
            
        users_collection.update_one({"_id": user_id}, {"$set": {attr.lower(): value}})

        # Fetch the updated personal info
        personal_info = get_personal_info(user_id)
        response = {
            'status': 'success',
            'message': 'User info updated successfully',
            'data': {
                'personal_info': personal_info,
            }
        }

        # Close the MongoDB connection
        mongo_conn.close()

        # Send the response
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
    
    def register_with_registry_center(self):
        self.registry_center_url = 'http://localhost:8000'
        try:
            response = requests.post(f'{self.registry_center_url}/inner-service/', json={
                'action': 'register',
                'service_name': 'user_service',
                'service_address': 'localhost:8001'
            })
            if response.status_code == 200:
                print('User Server registered with Registry Center')
            else:
                print('Failed to register with Registry Center')
        except requests.RequestException as e:
            print(f'Error registering with Registry Center: {e}')

    def query_registry_center_for_service(self, service_name):
        try:
            response = requests.get(f'{self.registry_center_url}/inner-services/{service_name}')
            if response.status_code == 200:
                service_info = response.json()
                return service_info.get('address')
            else:
                print('Failed to retrieve service address from Registry Center')
                return None
        except requests.RequestException as e:
            print(f'Error querying Registry Center: {e}')
            return None


if __name__ == "__main__":
    server = HTTPServer(('localhost', 8001), AggieBookUserServer)
    user_server = AggieBookUserServer
    user_server.register_with_registry_center(user_server)
    print(" --- AggieBook UserServer set up successfully. ---")
    server.serve_forever()
