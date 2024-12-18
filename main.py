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
    status, headers, body = handleRequest(request)

    # Prepare the HTTP response message
    response = "HTTP/1.1 " + status + "\r\n" + headers + "\r\n\r\n"
    response = response.encode("utf-8")
    if (isinstance(body, str)):
        body = body.encode("utf-8")
    response = response + body

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
                status = "200 OK"
                headers = "Content-Type: text/csv; charset=UTF-8"
                body = content
            except FileNotFoundError:
                status = "404 NOT FOUND"
                headers = "Content-Type: text/plain; charset=UTF-8"
                body = "Unfortunately, the file couldn't be found. Please try again if you want."

    # Return data.csv file to download
    elif path == "/data.csv":
        try:
            file = open("data.csv", "r", encoding="utf-8")
            content = file.read()
            file.close()
            status = "200 OK"
            headers = "Content-Type: text/csv; charset=UTF-8"
            body = content
        except FileNotFoundError:
            status = "404 NOT FOUND"
            headers = "Content-Type: text/plain; charset=UTF-8"
            body = "Unfortunately, the file couldn't be found. Please try again if you want."

    # Return assets from static folder (e.g. images)
    elif path.startswith("/static/"):
        path = path.lstrip("/")
        if os.path.exists(path) and not os.path.isdir(path): # don't serve directories
            contentType = mimetypes.guess_type(path)[0] or 'text/html'
            with open(path, 'rb') as f:
                content = f.read()
            status = "200 OK"
            headers = "Content-Type: " + contentType + "; charset=UTF-8"
            body = content
        else:
            status = "404 NOT FOUND"
            headers = "Content-Type: text/plain; charset=UTF-8"
            body = "Unfortunately, the file couldn't be found. Please try again if you want."

    # Otherwise, return homepage
    else:
        try:
            file = open("index.htm", "r", encoding="utf-8")
            content = file.read()
            file.close()
            status = "200 OK"
            headers = "Content-Type: text/html; charset=UTF-8"
            body = content
        except FileNotFoundError:
            status = "404 NOT FOUND"
            headers = "Content-Type: text/plain; charset=UTF-8"
            body = "Unfortunately, the file couldn't be found. Please try again if you want."

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
                        status = "303 See Other"
                        headers = "Location: /?submissionStatus=success"
                        body = "Please wait..."
                    except (IOError, OSError):
                        status = "303 See Other"
                        headers = "Location: /?submissionStatus=failed"
                        body = "Please wait..."
        except (FileNotFoundError, PermissionError, OSError):
            status = "303 See Other"
            headers = "Location: /?submissionStatus=failed"
            body = "Please wait..."
        
  return status, headers, body

def startServer():
    # Define socket host and port
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 8080

    # Create server socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((SERVER_HOST, SERVER_PORT))
    serverSocket.listen(1)
    print('Listening on port %s...' % SERVER_PORT)

    while True:
        # Client
        clientConnection, clientAddress = serverSocket.accept()
        # Allow for multi-threading
        threading.Thread(target=handleClient, args=(clientConnection,)).start()

if __name__=="__main__":
    startServer()