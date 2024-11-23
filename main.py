# John Doan - CSCI 4550 Project
import socket
import threading
# Made from SCRATCH
# No web frameworks (e.g. Django/Node.js) or use Python web modules
# like HTTPServer for this project

# Create a Lock to prevent threads from overwriting file
fileLock = threading.Lock()

# Convert the form data into an easy to read dictionary
def readFormData(formData):
    pairs = formData.split('&')
    dictionary = {}
    for pair in pairs:
        if '=' in pair:
            name, value = pair.split('=', 1)
            dictionary[name] = value
    return dictionary

# Handle each client
def handleClient(clientConnection):
    # Make sure we get all packets
    request = b''
    while True:
        chunk = clientConnection.recv(1024)  # Receive in chunks
        request += chunk
        if len(chunk) < 1024:  # Stop when no more data is available
            break

    # Process the request
    request = request.decode("utf-8")
    print(request)
    response = handleRequest(request)

    # Close socket
    clientConnection.sendall(response.encode())
    clientConnection.close()

# Handle the HTTP request
def handleRequest(request):
  requestMethod = request.split(' ')[0]
  filename = request.split('\n')[0].split()[1]

  # Return file to user
  if requestMethod == "GET":
    if filename == '/data':
        # Return data file
        with fileLock:
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
  elif requestMethod == "POST" and filename == '/':
    #Luckily, the header and body of the HTTP request are separated by \r\n\r\n
    body = request.split('\r\n\r\n')[1]
    result = readFormData(body)
    
    # Write data to file
    with fileLock:
        try:
            with open("data.csv", "a") as dataFile:
                if bool(result):
                    try:
                        dataFile.write("\n" + result.get("timestamp", "") + "," + result.get("zipCode", "") + "," + result.get("temperature", ""))
                    except (IOError, OSError):
                        response = (
                            "HTTP/1.1 303 See Other\r\n"
                            "Location: /?submissionStatus=failed\r\n\r\n")
        except (FileNotFoundError, PermissionError, OSError):
            response = (
            "HTTP/1.1 303 See Other\r\n"
            "Location: /?submissionStatus=failed\r\n\r\n")
            
        response = (
            "HTTP/1.1 303 See Other\r\n"
            "Location: /?submissionStatus=success\r\n\r\n")
        
  return response

def startServer():
    # Define socket host and port
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 8080

    # Create server socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((SERVER_HOST, SERVER_PORT))
    serverSocket.listen(1)
    print('Listening on port %s ...' % SERVER_PORT)

    while True:
        # Client
        clientConnection, clientAddress = serverSocket.accept()
        # Allow for multi-threading
        threading.Thread(target=handleClient, args=(clientConnection,)).start()

if __name__=="__main__":
    startServer()
