
# HTTP-Like Server System

## Overview
This project simulates an HTTP server in Python. It consists of a server that can handle HTTP GET requests for static files such as HTML, images, and redirections. Additionally, there is a client component designed to test the server's capabilities including persistent connections and reconnection capabilities. The project demonstrates fundamental networking concepts such as socket programming, request parsing, and response generation in a web context.

## Components

### Server
The server component listens for HTTP requests and serves files from a designated directory. It handles file not found errors and redirects.

- **Functionality**:
  - Listen on a specified TCP port.
  - Serve static files from a file directory.
  - Handle HTTP GET requests.
  - Respond with appropriate HTTP status codes such as 200 (OK), 404 (Not Found), and 301 (Moved Permanently).
  - Log request and response headers to the console.

### Client
The client component supports sending HTTP GET requests to the server. It demonstrates the ability to maintain persistent connections (`Connection: keep-alive`) and handles reconnections if the connection is lost.

- **Functionality**:
  - Send HTTP GET requests to a specified server IP and port.
  - Support for persistent connections using the `Connection: keep-alive` header.
  - Automatically reconnect and resend the last request if the connection is unexpectedly closed.

### Testing
Unit tests are provided to verify both the server's and client's behavior under various scenarios including handling of static files, redirects, and error conditions.

## How to Run

### Server
To start the server, use the following command, specifying the port number:
```bash
python3 server.py <server-port>
```

### Client
To start the client and connect to the server, use the following command:
```bash
python3 client.py <server-ip> <server-port>
```

### Testing
To run the tests, ensure you have the testing repository cloned and then execute the test script:
```bash
python3 test.py
```
For more detailed information on running the tests and additional test scenarios, please refer to the test repository at [GitHub Test Repository](https://github.com/RoeeHashai/Unittest-HTTP-TCP-Server-Client).
