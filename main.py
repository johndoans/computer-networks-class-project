# John Doan - CSCI 4550 Project
import mimetypes
import socket
import threading
import os

# Made from SCRATCH
# No web frameworks (e.g. Django/Node.js) or Python web modules
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

    # Encode data in bytes if HTTP response is in string format
    if (isinstance(response, str)):
        response = response.encode()

    # Close socket
    clientConnection.sendall(response)
    clientConnection.close()

# Handle the HTTP request
def handleRequest(request):
  # Manually read the HTTP request
  requestMethod = request.split(' ')[0]
  path = request.split('\n')[0].split()[1]

  # Return file to user
  if requestMethod == "GET":
    if path == "/data":
        # Return data file
        with fileLock:
            try:
                file = open("data.csv", "r", encoding="utf-8")
                content = file.read()
                file.close()
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=UTF-8\r\n\n" + content
            except FileNotFoundError:
                response = "HTTP/1.0 404 NOT FOUND\n\nFile Not Found"

    # Return data.csv file to download
    elif path == "/data.csv":
        try:
            file = open("data.csv", "r", encoding="utf-8")
            content = file.read()
            file.close()
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/csv; charset=UTF-8\r\n\n" + content
        except FileNotFoundError:
            response = "HTTP/1.0 404 NOT FOUND\n\nFile Not Found"

    # Return assets from static folder (e.g. images)
    elif path.startswith("/static/"):
        path = path.lstrip("/")
        if os.path.exists(path) and not os.path.isdir(path): # don't serve directories
            contentType = mimetypes.guess_type(path)[0] or 'text/html'
            with open(path, 'rb') as f:
                content = f.read()
            response = b"HTTP/1.1 200 OK\r\nContent-Type: " + str.encode(contentType) + b"; charset=UTF-8\r\n\n" + content
        else:
            response = "HTTP/1.0 404 NOT FOUND\n\nFile Not Found"

    # Otherwise, return homepage
    else:
        try:
            file = open("index.htm", "r", encoding="utf-8")
            content = file.read()
            file.close()
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n\n" + content
        except FileNotFoundError:
            response = "HTTP/1.0 404 NOT FOUND\n\nFile Not Found"

  # Handle user submitted data
  elif requestMethod == "POST" and path == '/':
    #Luckily, the header and body of the HTTP request are separated by \r\n\r\n
    body = request.split('\r\n\r\n')[1]
    result = readFormData(body)
    
    # Write data to file
    with fileLock:
        try:
            with open("data.csv", "a", encoding="utf-8") as dataFile:
                if bool(result):
                    try:
                        # Write the data in a CSV line
                        # No need to encode or escape special characters,
                        # since HTML form data is already encoded by the browser
                        dataFile.write("\n" + result.get("timestamp", "") + "," 
                                       + result.get("zipCode", "") + ","
                                       + result.get("temperature", "") + ","
                                       + result.get("windDirection", "") + ","
                                       + result.get("windSpeed", "") + ","
                                       + result.get("condition", "") + ","
                                       + result.get("description", ""))
                        
                        # Reload homepage and add query param so homepage knows to show success message
                        response = ("HTTP/1.1 303 See Other\r\n"
                                    "Location: /?submissionStatus=success\r\n\r\n")
                    except (IOError, OSError):
                        response = (
                            "HTTP/1.1 303 See Other\r\n"
                            "Location: /?submissionStatus=failed\r\n\r\n")
        except (FileNotFoundError, PermissionError, OSError):
            response = (
            "HTTP/1.1 303 See Other\r\n"
            "Location: /?submissionStatus=failed\r\n\r\n")
        
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