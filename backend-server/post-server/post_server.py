
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from socketserver import BaseServer
from dbOps import *
import requests

CLIENT_ADDRESS = "../frontend-web/"

class AggieBookPostServer(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server: BaseServer) -> None:
        super().__init__(request, client_address, server)
        self.registry_center_url = 'http://localhost:8000'

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_body = json.loads(post_data)

        print(f"content_length {content_length}")
        print(f"post_data {post_data}")
        print(f"post_body {post_body}")

        if self.path == '/posts/newstory':
            # Handle new story submission
            self.handle_newstory(post_body)
        elif self.path == '/posts/like':
            self.handle_toggle_like(post_body)
        elif self.path == '/posts/comment':
            self.handle_comment(post_body)
        else:
            self.send_error(404, "Endpoint not found.")


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

    def handle_toggle_like(self, post_body):
        userID = post_body['userID']
        postID = post_body['postID']
        
        toggle_like(userID=userID, post_id=postID)

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

    def handle_comment(self, post_body):
        userID = post_body['userID']
        postID = post_body['postID']
        content = post_body['content']
        comment(userID=userID, post_id=postID, content=content)
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

    def register_with_registry_center(self):
        self.registry_center_url = 'http://localhost:8000'
        try:
            response = requests.post(f'{self.registry_center_url}/inner-service/', json={
                'action': 'register',
                'service_name': 'post_service',
                'service_address': 'localhost:8002'
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

    server = HTTPServer(('localhost', 8002), AggieBookPostServer)
    post_server = AggieBookPostServer
    post_server.register_with_registry_center(post_server)
    print(" --- AggieBook PostServer set up successfully. ---")
    server.serve_forever()