import socket
#I guess we can't use web frameworks (e.g. Django/Node.js) or use Python modules like HTTPServer for this project, so we have to do it from scratch
def handle_request(request):
  #Send the HTML file so the user can actually see something
  #At this point, there is only one html file for this "website"
    try:
        file = open('index.htm')
        content = file.read()
        file.close()
        response = 'HTTP/1.0 200 OK\n\n' + content
    except FileNotFoundError:
        response = 'HTTP/1.0 404 NOT FOUND\n\nFile Not Found'
    return response

# Define socket host and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8080

# Create server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)
print('Listening on port %s ...' % SERVER_PORT)

while True:
    # Client
    client_connection, client_address = server_socket.accept()
    request = client_connection.recv(1024).decode()
    print(request)

    response = handle_request(request)
    client_connection.sendall(response.encode())

    client_connection.close()

# Close socket
server_socket.close()
