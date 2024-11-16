from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import mugsworth  # Assuming mugsworth.getSpeech() generates audio content

class AudioServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/cgi-bin/mugsworth.cgi":
            try:
                # Get the audio content from mugsworth
                audio_content = mugsworth.getSpeech()

                # Determine the length of the audio content
                content_length = len(audio_content)

                # Send HTTP response headers
                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Length", str(content_length))
                self.end_headers()

                # Send the audio content to the client
                self.wfile.write(audio_content)
                print(f"Sent {content_length} bytes of audio data")

            except Exception as e:
                # Handle errors gracefully
                print(f"Error occurred: {e}")
                self.send_response(500)
                self.end_headers()
                error_message = f"Internal Server Error: {e}"
                self.wfile.write(error_message.encode())
        else:
            # For any other paths, return 404 Not Found
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

if __name__ == "__main__":
    # Set up the HTTP server to run on port 8000
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, AudioServerHandler)
    print("Starting server on port 8000...")
    httpd.serve_forever()
