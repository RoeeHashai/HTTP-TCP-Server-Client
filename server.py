import os
import socket
import sys
def read_file_content(filename):
    """
    Read the content of a file and return it as a string if a text file, or as bytes if an image file.
    Returns:
        content (bytes): The content of the file.
    """
    base_dir = 'files'
    if filename == '/':
        filename = '/index.html'
    elif not filename.startswith('/') or filename.endswith('/'):
        return 'Not Found'

    file_path = os.path.join(base_dir, filename.strip('/'))
    if not os.path.exists(file_path) or os.path.isdir(file_path):
        return 'Not Found'
    mode = 'rb' if file_path.endswith(('.jpg', '.jpeg', '.png', 'ico')) else 'r'
    with open(file_path, mode) as f:
        content = f.read()
    return content.encode() if mode == 'r' else content

def send_all(sock, data):
    """
    Send all the data to the socket.
    Returns: None
    """
    bytes_sent = 0
    while bytes_sent < len(data):
        sent = sock.send(data[bytes_sent:])
        if not sent:
            break
        bytes_sent += sent

def read_header(client_socket, buffer):
    """
    Read the header from the client socket.
    Returns:
        header (str): The header of the request.
        buffer (str): The buffer containing the rest of the data.
        connection_alive (bool): True if the connection is still alive, False otherwise.
    """
    connection_alive = True
    header = ''
    while '\r\n\r\n' not in buffer:
        try:
            data = client_socket.recv(BUFFER_READ_SIZE).decode()
            if not data:
                # print(f'[Connection] Received 0 bytes, closing connection with {client_address}')
                connection_alive = False
                client_socket.close()
                break
            buffer += data
        except socket.timeout:
            # print(f'[Connection] Timeout reading header, closing connection with {client_address}')
            connection_alive = False
            client_socket.close()
            break
    if '\r\n\r\n' in buffer:
            header, buffer = buffer.split('\r\n\r\n', 1)
    else:
        header = buffer
        buffer = ''
    return header, buffer, connection_alive    

def parse_header(header):
    """
    Parse the header and return the method, path, connection status, and content length.
    Returns:
        method (str): The method of the request.
        path (str): The path of the request.
        connection_status (str): The connection status of the request.
        content_length (int): The content length of the request.
    """
    headers = header.split('\r\n')
    method, path, connection_status, content_length = '', '', '', 0
    for line in headers:
        if line.startswith('GET'):
            method, path, _ = line.split(' ')
        elif line.startswith('Connection:'):
            connection_status = line.split(': ')[1]
        elif line.startswith('Content-Length:'):
            content_length = int(line.split(': ')[1])
    return method, path, connection_status, content_length

def read_body(client_socket, buffer, content_length):
    """
    Read the body from the client socket.
    Returns:
        body (str): The body of the request.
        buffer (str): The buffer containing the rest of the data.
        connection_alive (bool): True if the connection is still alive, False otherwise.
    """
    connection_alive = True
    while len(buffer) < content_length:
        try:
            data = client_socket.recv(BUFFER_READ_SIZE).decode()
            if not data:
                # print(f'[Connection] Received 0 bytes reading the body, closing connection with {client_address}')
                connection_alive = False
                client_socket.close()
                break
            buffer += data
        except socket.timeout:
            # print(f'[Connection] Timeout reading body, closing connection with {client_address}')
            connection_alive = False
            client_socket.close()
            break
    # build the body and the next request buffer
    next_data = buffer[content_length:]
    body = buffer[:content_length]
    buffer = next_data
    return body, buffer, connection_alive

def process(client_socket, path, connection_status):
    """
    Process the request and return the response.
    Returns:
        connsction_status (str): The connection status of the response.
    """
    if path == '/redirect':
            code = 301
            connection_status = 'close'
            location = '/result.html'
    else:
        res_body = read_file_content(path)
        if res_body == 'Not Found':
            code = 404
            connection_status = 'close'
        else:
            code = 200
    description = {
        200: 'OK',
        301: 'Moved Permanently',
        404: 'Not Found'
    }
    # build the response
    response_header = f'HTTP/1.1 {code} {description[code]}\r\n'
    response_header += f'Connection: {connection_status}\r\n'
    if code == 301:
        response_header += f'Location: {location}\r\n'
    elif code == 200:
        response_header += f'Content-Length: {len(res_body)}\r\n'
    response_header += '\r\n'
    response = response_header.encode() + (res_body if code == 200 else b'')
    # print(f'[Response]\n{response}\n[End-Response]')
    # send the response and close the connection if needed
    send_all(client_socket, response)
    return connection_status


PORT = int(sys.argv[1])
BUFFER_READ_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', PORT))
s.listen(1)
# print(f'[Server] Listening on port {PORT}')

while True:
    client_socket, client_address = s.accept()
    # print(f'[Server] New Connection from {client_address}')
    client_socket.settimeout(1) # NEED TO CHANGE BEFORE SUBMISSION
    connection_alive = True
    buffer = ''
    while connection_alive:
        header, body = '', ''
        # read the header
        header, buffer, connection_alive = read_header(client_socket, buffer)
        if not connection_alive:
            break
        # print(f'[Request-Header]\n{header}\n[End-Request-Header]')
        print(header)
        # parse the header
        method, path, connection_status, content_length = parse_header(header)
        # read the body
        body, buffer, connection_alive = read_body(client_socket, buffer, content_length)
        if not connection_alive:
            break
        print(body)
        # print(f'[Request-Body]\n{body}\n[End-Request-Body]')
        # print(f'[Buffer] Buffer for next request:\n{buffer}\n[End-Buffer]')
        
        # process the request
        connection_status = process(client_socket, path, connection_status)
        # print(f'[Connection] Response sent to {client_address}')
        if connection_status == 'close':
            # print(f'[Connection] Closing connection with {client_address}')
            connection_alive = False
            client_socket.close()
            break