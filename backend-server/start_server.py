import subprocess
import sys
import os

def start_server(script_name):
    # Runs the Python script in a new process
    try:
        subprocess.Popen([sys.executable, script_name], creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
        print(f"Failed to start {script_name}: {str(e)}")

if __name__ == "__main__":
    # The paths to the service scripts
    registry_center_path = os.path.join('registry-center', 'registry_center.py')
    user_server_path = os.path.join('user-server', 'user_server.py')
    post_server_path = os.path.join('post-server', 'post_server.py')

    print("Starting all servers...")

    # Start Registry Center
    start_server(registry_center_path)

    # Start User Server
    start_server(user_server_path)

    # Start Post Server
    start_server(post_server_path)