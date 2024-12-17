import os
import socket
import sys

def send_request(sock, path):
    """
    Send an HTTP GET request to the specified path.
    Returns:
        sock (socket): Socket object after sending.
    Raises:
        ConnectionResetError: If the connection is reset during send.
    """
    http_req = f'GET {path} HTTP/1.1\r\nHost: {IP}:{PORT}\r\nConnection: keep-alive\r\nContent-Length: 0\r\n\r\n'
    # print(f"[Send Request] Sending request for path: {path}")
    try:
        sock.sendall(http_req.encode())
        # print("[Send Request] Request sent successfully.")
    except ConnectionResetError as e:
        # print(f"[Send Requset] Connection reset while sending: {e}")
        raise
    except socket.error as e:
        # print(f"[Send Request] Error sending request: {e}")
        raise
    return sock

def receive_response(sock, buffer):
    """
    Receive and return the HTTP response.
    Returns:
        response (str): The response data as a string.
    Raises:
        ConnectionResetError: If the connection is reset during receive.
    """
    try:
        while b'\r\n\r\n' not in buffer:
            part = sock.recv(1024)
            if not part:  # Connection closed
                raise ConnectionResetError("[Receive Response] Server closed the connection while receiving.")
            buffer.extend(part)
    except ConnectionResetError as e:
        # print(f"[Receive Response] Connection reset while receiving: {e}")
        raise
    except socket.error as e:
        # print(f"[Receive Response] Socket error during receive: {e}")
        raise

    parts = buffer.split(b'\r\n\r\n', 1)
    header = parts[0]
    body = parts[1] if len(parts) > 1 else bytearray()
    headers = header.decode().split('\r\n')
    code = 0
    content_length = 0
    location = ''
    for h in headers:
        if h.startswith('HTTP/1.1'):
            code = int(h.split(' ')[1])
        if h.startswith('Content-Length:'):
            content_length = int(h.split(' ')[1])

        if h.startswith('Location:'):
            location = h.split(': ')[1]
    try:
        while len(body) < content_length:
            part = sock.recv(1024)
            if not part:
                raise ConnectionResetError("[Receive Response] Server closed the connection while receiving the body.")
            body.extend(part)
    except ConnectionResetError as e:
        # print(f"[Receive Response] Connection reset while receiving: {e}")
        raise
    except socket.error as e:
        # print(f"[Receive Response] Socket error during receive: {e}")
        raise
    return headers[0], body[:content_length], body[content_length:], code, location

def reconnect_socket(sock):
    """
    Reconnects to the server and returns a new socket.
    """
    sock.close()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((IP, PORT))
    # print("[Control] Reconnected to the server.")
    return sock

def main():
    global IP, PORT
    IP = sys.argv[1]
    PORT = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    last_path = None 
    buffer = bytearray()
    while True:
        if last_path is None:
            path = input()
        else:
            # Retransmit the previous request
            path = last_path
            # print(f"[Main] Retransmitting the previous path: {path}")
        try:
            # Attempt to send the request
            s = send_request(s, path)
            # Receive the response
            top_header, body, buffer, code, location = receive_response(s, buffer)
            print(top_header)
            if code == 200:
                if path == '/':
                    path = '/index.html'
                filename = os.path.basename(path)
                with open(filename, 'wb') as f:
                    f.write(body)                
                # Clear the last_path after a successful request-response cycle
                last_path = None
            elif code == 301:
                # print(f"[Response] Redirecting to {location}")
                s = reconnect_socket(s)
                buffer = bytearray()
                last_path = location
            elif code == 404:
                # print("[Response] Not Found")
                last_path = None                
                
        except ConnectionResetError:
            # print("[Control] Connection reset detected. Reconnecting and retransmitting...")
            s = reconnect_socket(s)
            buffer = bytearray()
            last_path = path

        except socket.error as e:
            # print(f"[Control] An unexpected error occurred: {e}")
            s = reconnect_socket(s)
            buffer = bytearray()
            last_path = path

if __name__ == '__main__':
    main()
