from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
from urllib.parse import urlparse, parse_qs


CLIENT_ADDRESS = "../frontend-web/"
class RegistryCenter(BaseHTTPRequestHandler):
    services = {}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path in ('/', '/login'):
            self.serve_static_file('login.html')
        elif self.path in ('/register'):
            self.serve_static_file('register.html')
        elif self.path.endswith('.html') or self.path.endswith('.css') or self.path.endswith('.js') or self.path.endswith('.jpg'):
            self.serve_static_file(self.path)
        elif self.path.startswith("/inner-service/"):
            self.query_service_handler()
        else:
            self.send_error(404, "File not found.")

    def do_PUT(self):
        path = self.path
        if path.startswith('/users/'):
            self.forward_request('user_service', request_method=requests.put)
        elif path.startswith('/posts/'):
            self.forward_request('post_service', request_method=requests.put)
        else:
            self.send_error(404, "Service not found.")
    
    def do_POST(self):
        path = self.path
        if path.startswith('/users/'):
            self.forward_request('user_service', request_method=requests.post)
        elif path.startswith('/posts/'):
            self.forward_request('post_service', request_method=requests.post)
        elif path.startswith('/inner-service/'):
            self.registry_handler()
        else:
            self.send_error(404, "Service not found.")

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

    def forward_request(self, service_name, request_method):
        # print(f"services {self.services}")
        service_address = self.services.get(service_name)
        if not service_address:
            self.send_error(404, 'Service not registered.')
            return
        
        # Parse the query string
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)

        # Get the full URL to forward the request to
        forward_url = f'http://{service_address}{parsed_path.path}'
        
        # Prepare headers for forwarding
        forward_headers = {key: val for key, val in self.headers.items()}
        
        # Read the request body if present
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length else None
        print(f"post data {post_data}")

        try:
            # Forward the request to the service and get the response
            response = request_method(forward_url, data=post_data, headers=forward_headers, params=query)
            # Write the response back to the client
            self.send_response(response.status_code)
            for header_key, header_value in response.headers.items():
                self.send_header(header_key, header_value)
            self.end_headers()
            self.wfile.write(response.content)
            
        except requests.RequestException as e:
            self.send_error(500, f'Error forwarding request: {e}')


    def registry_handler(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_body = json.loads(post_data.decode('utf-8'))

        action = post_body.get('action')
        service_name = post_body.get('service_name')
        service_address = post_body.get('service_address')
        # print(f"action {action} service_name {service_name} service_address {service_address}")
        if action == 'register' and service_name and service_address:
            self.services[service_name] = service_address
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({'message': f'Service {service_name} registered successfully'}).encode('utf-8'))
        elif action == 'unregister' and service_name:
            self.services.pop(service_name, None)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({'message': f'Service {service_name} unregistered successfully'}).encode('utf-8'))
        else:
            self.send_error(400, 'Invalid request')
        print(f"service {service_name} registered with address {service_address}")
        print(f"current services {self.services}")

if __name__ == "__main__":
    server = HTTPServer(('localhost', 8000), RegistryCenter)
    server.serve_forever()
