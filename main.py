# John Doan - CSCI 4550 Project
import socket
# Made from SCRATCH
# I guess we can't use web frameworks (e.g. Django/Node.js) or use Python modules
# like HTTPServer for this project, so we have to do it from scratch

# Convert the form data into an easy to read dictionary
def readFormData(formData):
    pairs = formData.split('&')
    dictionary = {}
    for pair in pairs:
        if '=' in pair:
            name, value = pair.split('=', 1)
            dictionary[name] = value
    return dictionary

# Handle the HTTP request
def handle_request(request):
  request_method = request.split(' ')[0]
  filename = request.split('\n')[0].split()[1]

  # Return file to user
  if request_method == "GET":
    if filename == '/data':
        # Return data file
        try:
            file = open('data.csv')
            content = file.read()
            file.close()
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=UTF-8\r\n\n" + content
        except FileNotFoundError:
            response = 'HTTP/1.0 404 NOT FOUND\n\nFile Not Found'
    else:
        # Return homepage
        try:
            file = open('index.htm')
            content = file.read()
            file.close()
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n\n" + content
        except FileNotFoundError:
            response = 'HTTP/1.0 404 NOT FOUND\n\nFile Not Found'

  # Handle user submitted data
  elif request_method == "POST" and filename == '/':
    #Luckily, the header and body of the HTTP request are separated by \r\n\r\n
    body = request.split('\r\n\r\n')[1]
    result = readFormData(body)

    # Write data to file
    with open("data.csv", "a") as myfile:
        myfile.write("\n" + result["timestamp"] + "," + result["zipCode"] + "," + result["temperature"])
    file = open('index.htm')
    content = file.read()
    file.close()

    # Response to user
    successText = "<div id='successNotification'>Data submitted successfully!</div><br>";
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n\n" + successText + content
        
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

    # Make sure we get all packets
    request = b''
    while True:
        chunk = client_connection.recv(1024)  # Receive in chunks
        request += chunk
        if len(chunk) < 1024:  # Stop when no more data is available
            break

    # Process the request
    request = request.decode("utf-8")
    print(request)
    response = handle_request(request)

    # Close socket
    client_connection.sendall(response.encode())
    client_connection.close()