import unittest
import subprocess
import time
import os
import socket

class TestServerClientInteraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the client
        cls.client_process = subprocess.Popen(
            ['python3', 'client.py', 'localhost', '8000'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(1)
        # Open log file
        cls.log_file = open('client_out.log', 'a')

    @classmethod
    def tearDownClass(cls):
        # Terminate the client after all tests
        cls.client_process.terminate()
        cls.client_process.wait()
        cls.client_process.stdin.close()
        cls.client_process.stdout.close()
        cls.client_process.stderr.close()
        cls.log_file.close()

    def log_interaction(self, request, response):
        """Logs the request and response to a file."""
        self.log_file.write(f"{request}\n{response}")
        self.log_file.flush()
        
    def send_request_and_receive_response(self, path):
        """Utility method to send a request and receive a response from the client."""
        self.client_process.stdin.write(f'{path}\n')
        self.client_process.stdin.flush()
        response = self.client_process.stdout.readline()
        # Log the request and response
        self.log_interaction(path, response)
        return response
    
    def test1(self):
        """Test retrieving an existing file from the server."""
        path = '/index.html'
        filename = 'index.html'
        response = self.send_request_and_receive_response(path)
        self.assertIn('HTTP/1.1 200 OK', response, '[TEST 1] Header was not printed correctly')
        self.assertTrue(os.path.exists(filename), "[TEST 1] /index.html file not created by the client")

        with open(filename, 'r') as file:
            retrieved_contents = file.read()
        expected_file_path = 'files/index.html'
        with open(expected_file_path, 'r') as file:
            expected_contents = file.read()
        self.assertEqual(expected_contents, retrieved_contents, "[TEST 1] /index.html file content does not match the expected content")
        os.remove(filename)

    def test2(self):
        """Test retrieving a non-existing file from the server."""
        response = self.send_request_and_receive_response('/non_existent_file.html')
        self.assertIn('HTTP/1.1 404 Not Found', response, "[TEST 2] Non-existent file did not return correctly")
        
    def test3(self):
        """Test a redirect response from the server."""
        response = self.send_request_and_receive_response('/redirect')
        self.assertIn('HTTP/1.1 301 Moved Permanently', response, "[TEST 3] Redirect response did not return correctly")
        response = self.client_process.stdout.readline()
        self.assertIn('HTTP/1.1 200 OK', response, "[TEST 3] Redirected file did not return correctly")
        filename = 'result.html'
        self.assertTrue(os.path.exists(filename), "[TEST 3] /result.html file not created by the client")
        with open(filename, 'r') as file:
            retrieved_contents = file.read()
        expected_file_path = 'files/result.html'
        with open(expected_file_path, 'r') as file:
            expected_contents = file.read()
        self.assertEqual(expected_contents, retrieved_contents, "[TEST 3] /result.html file content does not match the expected content")
        os.remove(filename)
        
        response = self.send_request_and_receive_response('redirect')
        self.assertIn('HTTP/1.1 301 Moved Permanently', response, "[TEST 3] Redirect response did not return correctly")
        response = self.client_process.stdout.readline()
        self.assertIn('HTTP/1.1 200 OK', response, "[TEST 3] Redirected file did not return correctly")
        filename = 'result.html'
        self.assertTrue(os.path.exists(filename), "[TEST 3] /result.html file not created by the client")
        with open(filename, 'r') as file:
            retrieved_contents = file.read()
        expected_file_path = 'files/result.html'
        with open(expected_file_path, 'r') as file:
            expected_contents = file.read()
        self.assertEqual(expected_contents, retrieved_contents, "[TEST 3] /result.html file content does not match the expected content")
        os.remove(filename)
        
    def test4(self):
        """Test checks differnt requests of files to the server one after the other"""
        list_files = ['/index.html', 'index.html','/a/b/ref.html','/c/footube.css','c/Footube.html','/c/footube.js','/result.html', '/', '']
        for path in list_files:
            response = self.send_request_and_receive_response(path)
            self.assertIn('HTTP/1.1 200 OK', response, f"[TEST 4] did not return correctly for {path}")
            # Ensure the file was created by the client
            path = path.strip()
            if not path.startswith('/'):
                path = '/' + path
            if path == '/':
                path = '/index.html'
            filename = path.split('/')[-1]
            self.assertTrue(os.path.exists(filename), f"[TEST 4] {path} file not created by the client")
            with open(filename, 'r') as file:
                retrieved_contents = file.read()
            # Check if the content of the file is correct
            expected_file_path = f'files{path}'
            with open(expected_file_path, 'r') as file:
                expected_contents = file.read()
            self.assertEqual(expected_contents, retrieved_contents, f"[TEST 4] {path} file content does not match the expected content")
            # Clean up by removing the file after the test
            os.remove(filename)
      
    def test5(self):
        """Test with images"""
        list_files = ['/a/1.jpg','a/2.jpg','/a/3.jpg','/a/4.jpg','a/5.jpg','/a/6.jpg','/a/b/1.jpg','a/b/2.jpg','/a/b/3.jpg','/a/b/4.jpg','/a/b/5.jpg','/a/b/6.jpg', '/c/img/1.jpg','/c/img/2.jpg','/c/img/3.jpg','/c/img/4.jpg','/c/img/5.jpg','/c/img/6.jpg', '/favicon.ico']
        for path in list_files:
            response = self.send_request_and_receive_response(path)
            self.assertIn('HTTP/1.1 200 OK', response)
            # Ensure the file was created by the client
            filename = path.split('/')[-1]
            self.assertTrue(os.path.exists(filename), f"[TEST 5] {path} file not created by the client")
            with open(filename, 'rb') as file:
                retrieved_contents = file.read()
            if not path.startswith('/'):
                path = '/' + path
            expected_file_path = f'files{path}'
            with open(expected_file_path, 'rb') as file:
                expected_contents = file.read()
            self.assertEqual(expected_contents, retrieved_contents, f"[TEST 5] {path} file content does not match the expected content")
            # Clean up by removing the file after the test
            os.remove(filename)
    
    def test6(self):
        """Test 404 Not Found - send bad requests to server"""
        bad_req = ['Roee','//','///','/////','bad.html','/a','/a/b','/a/b/','/a/b/1','/a/b/1.','/a/b/1.j','/a/b/1.jp','index.html/']
        for path in bad_req:
            response = self.send_request_and_receive_response(path)
            self.assertIn('HTTP/1.1 404 Not Found', response)

    def test7(self):
        """Test Timeout from the server"""
        req = '/'
        response = self.send_request_and_receive_response(req)
        self.assertIn('HTTP/1.1 200 OK', response)
        time.sleep(2)
        # Make sure this is on a new conenction using wireshark
        req = '/'
        response = self.send_request_and_receive_response(req)
        self.assertIn('HTTP/1.1 200 OK', response)
        os.remove('index.html')
        
    def test8(self):
        """Test that requests both images and text one after the other"""
        list_files = ['/index.html', '/a/1.jpg','/result.html','/a/b/1.jpg','a/b/ref.html','/a/2.jpg','c/footube.css']
        for path in list_files:
            mode = 'rb' if path.endswith(('.png', '.jpg', '.jpeg','ico')) else 'r'
            response = self.send_request_and_receive_response(path)
            self.assertIn('HTTP/1.1 200 OK', response)
            # Ensure the file was created by the client
            filename = path.split('/')[-1]
            self.assertTrue(os.path.exists(filename), f"[TEST 8] {path} file not created by the client")
            with open(filename, mode) as file:
                retrieved_contents = file.read()
            if not path.startswith('/'):
                path = '/' + path
            expected_file_path = f'files{path}'
            with open(expected_file_path, mode) as file:
                expected_contents = file.read()
            self.assertEqual(expected_contents, retrieved_contents, f"[TEST 8] {path} file content does not match the expected content")
            # Clean up by removing the file after the test
            os.remove(filename)
    
    def test9(self):
        """Test the transfer of large files"""
        large_file_path = 'files/large_file.txt'
        with open(large_file_path, 'w') as file:
            file.write('Hello World!' * 100000000)
        response = self.send_request_and_receive_response('/large_file.txt')
        self.assertIn('HTTP/1.1 200 OK', response)
        # Ensure the file was created by the client
        filename = 'large_file.txt'
        self.assertTrue(os.path.exists(filename), "[TEST 9] /large_file.txt file not created by the client")
        with open(filename, 'r') as file:
            retrieved_contents = file.read()
        with open(large_file_path, 'r') as file:
            expected_contents = file.read()
        self.assertEqual(expected_contents, retrieved_contents, "[TEST 9] /large_file.txt file content does not match the expected content")
        os.remove(filename)
        os.remove(large_file_path)
        
    def test10(self):
        """Test handling of concurrent requests to the server and validate file integrity."""
        def make_request(path):
            resp = self.send_request_and_receive_response(path)
            self.assertIn('HTTP/1.1 200 OK', resp)
            # Retrieve the filename from the path and check file existence
            filename = path.split('/')[-1]
            self.assertTrue(os.path.exists(filename), f"{filename} not created")
            mode = 'rb' if path.endswith(('.png', '.jpg', '.jpeg','ico')) else 'r'
            # Compare the contents of the downloaded file with the original
            with open(f'files{path}', mode) as original_file:
                original_content = original_file.read()
            with open(filename, mode) as downloaded_file:
                downloaded_content = downloaded_file.read()
            self.assertEqual(original_content, downloaded_content, f"Content mismatch for {filename}")
            # Clean up by removing the file after verification
            os.remove(filename)
            
        from threading import Thread
        paths = ['/index.html', '/a/1.jpg', '/c/footube.css']
        threads = [Thread(target=make_request, args=(path,)) for path in paths]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
            
    def test11(self):
        """Test to check that the server is reading the files in the correct format (comparing text read as bytes)."""
        # HTML file
        text_file_path = '/index.html'
        response = self.send_request_and_receive_response(text_file_path)
        self.assertIn('HTTP/1.1 200 OK', response)
        # Ensure the file was created by the client
        filename = text_file_path.split('/')[-1]
        self.assertTrue(os.path.exists(filename), f"[TEST 11] {text_file_path} file not created by the client")
        # Read the file saved by the client in binary mode
        with open(filename, 'rb') as file:
            retrieved_contents = file.read()
        # Open the source file in text mode, read, and encode to bytes
        expected_file_path = f'files{text_file_path}'
        with open(expected_file_path, 'r') as file:
            # Read the file content as string, then encode it to bytes
            expected_contents = file.read().encode()
        # Compare the bytes
        self.assertEqual(expected_contents, retrieved_contents, f"[TEST 11] {text_file_path} file content does not match the expected content")
        
        # Image file
        img_file_path = '/favicon.ico'
        response = self.send_request_and_receive_response(img_file_path)
        self.assertIn('HTTP/1.1 200 OK', response)
        # Ensure the file was created by the client
        filename = img_file_path.split('/')[-1]
        self.assertTrue(os.path.exists(filename), f"[TEST 11] {img_file_path} file not created by the client")
        with open(filename, 'rb') as file:
            retrieved_contents = file.read()
        expected_file_path = f'files{img_file_path}'
        with open(expected_file_path, 'rb') as file:
            expected_contents = file.read()
        self.assertEqual(expected_contents, retrieved_contents, f"[TEST 11] {img_file_path} file content does not match the expected content")
        os.remove('index.html')
        os.remove('favicon.ico')
    
    def test12(self):
        """Test a very large HTTP header."""
        header = 'GET /index.html HTTP/1.1\r\n'
        header += 'Long-Header: ' + 'a' * 1000000 + '\r\n'
        header += 'Connection: keep-alive\r\n'
        header += '\r\n'
        socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_client.connect(('localhost', 8000))
        socket_client.send(header.encode())
        response = socket_client.recv(4096).decode()
        response = response.split('\r\n')[0]
        self.assertIn('HTTP/1.1 200 OK', response)
        socket_client.close()
    
    def test13(self):
        """Test a HTTP request with a body."""
        header = 'GET /index.html HTTP/1.1\r\n'
        header += 'Content-Length: 10\r\n'
        header += '\r\n'
        header += '0123456789'
        socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_client.connect(('localhost', 8000))
        socket_client.send(header.encode())
        response = socket_client.recv(4096).decode()
        response = response.split('\r\n')[0]
        self.assertIn('HTTP/1.1 200 OK', response)
        socket_client.close()
        
if __name__ == '__main__':
    unittest.main()