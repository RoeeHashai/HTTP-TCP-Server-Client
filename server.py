import os
import socket
import sys
def read_file_content(filename):
    """
    Read the content of a file and return it as a string if a text file, or as a binary if an image file.
    @param filename: The name of the file to read.
    """
    base_dir = 'files'
    if filename == '/':
        filename = '/index.html'
    file_path = os.path.join(base_dir, filename.strip('/'))
    if not os.path.exists(file_path):
        return 'Not Found'
    if filename.endswith(('jpg', 'ico')):
        mode = 'rb'
    else:
        mode = 'r'
    with open(file_path, mode) as f:
        content = f.read()
    return content

PORT = int(sys.argv[1])
BUFFER_READ_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', PORT))
s.listen(1)
print(f'[Server] Listening on port {PORT}')

while True:
    client_socket, client_address = s.accept()
    print(f'[Server] New Connection from {client_address}')
    client_socket.settimeout(10)
    connection_alive = True
    buffer = ''
    while connection_alive:
        header, body = '', ''
        # read the header
        while True:
            try:
                data = client_socket.recv(BUFFER_READ_SIZE).decode()
                if not data:
                    print(f'[Connection] Received 0 bytes, closing connection with {client_address}')
                    connection_alive = False
                    client_socket.close()
                    break
                buffer += data
                if '\r\n\r\n' in buffer:
                    header, rest = buffer.split('\r\n\r\n', 1)
                    break
            except socket.timeout:
                print(f'[Connection] Timeout reading header, closing connection with {client_address}')
                connection_alive = False
                client_socket.close()
                break
        if not connection_alive:
            break
        print(f'[Request-Header]\n{header}\n[End-Request-Header]')
        # parse the header
        headers = header.split('\r\n')
        method, path, connection_status, content_length = '', '', '', 0
        for line in headers:
            if line.startswith('GET'):
                method, path, _ = line.split(' ')
            elif line.startswith('Connection:'):
                connection_status = line.split(': ')[1]
            elif line.startswith('Content-Length:'):
                content_length = int(line.split(': ')[1])
        # read the body
        body = rest
        while len(body) < content_length:
            try:
                data = client_socket.recv(BUFFER_READ_SIZE).decode()
                if not data:
                    print(f'[Connection] Received 0 bytes reading the body, closing connection with {client_address}')
                    connection_alive = False
                    client_socket.close()
                    break
                body += data
            except socket.timeout:
                print(f'[Connection] Timeout reading body, closing connection with {client_address}')
                connection_alive = False
                client_socket.close()
                break
        if not connection_alive:
            break

        next_req = body[content_length:]
        body = body[:content_length]
        buffer = next_req
        print(f'[Request-Body]\n{body}\n[End-Request-Body]')
        print(f'[Buffer] Buffer for next request:\n{buffer}\n[End-Buffer]')      