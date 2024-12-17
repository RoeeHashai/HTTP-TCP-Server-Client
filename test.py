import unittest
import subprocess
import time
import os

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
        self.assertIn('HTTP/1.1 301 Moved Permanently', response, "[TEST REDIRECT] Redirect response did not return correctly")
        response = self.client_process.stdout.readline()
        self.assertIn('HTTP/1.1 200 OK', response, "[TEST REDIRECT] Redirected file did not return correctly")
        filename = 'result.html'
        self.assertTrue(os.path.exists(filename), "[TEST REDIRECT] /result.html file not created by the client")
        with open(filename, 'r') as file:
            retrieved_contents = file.read()
        expected_file_path = 'files/result.html'
        with open(expected_file_path, 'r') as file:
            expected_contents = file.read()
        self.assertEqual(expected_contents, retrieved_contents, "[TEST REDIRECT] /result.html file content does not match the expected content")
        os.remove(filename)
        
    def test4(self):
        """Test checks 6 differnt requests of files to the server one after the other."""
        list_files = ['/index.html','/a/b/ref.html','/c/footube.css','/c/Footube.html','/c/footube.js','/result.html']
        for path in list_files:
            response = self.send_request_and_receive_response(path)
            self.assertIn('HTTP/1.1 200 OK', response)
            # Ensure the file was created by the client
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
        list_files = ['/a/1.jpg','/a/2.jpg','/a/3.jpg','/a/4.jpg','/a/5.jpg','/a/6.jpg','/a/b/1.jpg','/a/b/2.jpg','/a/b/3.jpg','/a/b/4.jpg','/a/b/5.jpg','/a/b/6.jpg', '/c/img/1.jpg','/c/img/2.jpg','/c/img/3.jpg','/c/img/4.jpg','/c/img/5.jpg','/c/img/6.jpg']
        for path in list_files:
            response = self.send_request_and_receive_response(path)
            self.assertIn('HTTP/1.1 200 OK', response)
            # Ensure the file was created by the client
            filename = path.split('/')[-1]
            self.assertTrue(os.path.exists(filename), f"[TEST 5] {path} file not created by the client")
            with open(filename, 'rb') as file:
                retrieved_contents = file.read()
            expected_file_path = f'files{path}'
            with open(expected_file_path, 'rb') as file:
                expected_contents = file.read()
            self.assertEqual(expected_contents, retrieved_contents, f"[TEST 5] {path} file content does not match the expected content")
            # Clean up by removing the file after the test
            os.remove(filename)
    
    def test6(self):
        """Test 404 Not Found - send bad requests to server"""
        bad_req = ['Roee','bad.html','/a','/a/b','/a/b/','/a/b/1','/a/b/1.','/a/b/1.j','/a/b/1.jp','//','index.html', 'index.html/', '/index.html/']
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

if __name__ == '__main__':
    unittest.main()