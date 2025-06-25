from http.server import BaseHTTPRequestHandler, HTTPServer
import mugsworth  # Assuming mugsworth.getSpeech() returns bytes of MP3 audio
import socket

def get_local_ip():
    """Get the actual local IP address (not 127.0.0.1)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to connect—just used to determine local IP
        s.connect(('10.255.255.255', 1))
        return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        s.close()

class AudioServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/cgi-bin/mugsworth.cgi":
            try:
                audio = mugsworth.getSpeech()
                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Length", str(len(audio)))
                self.end_headers()
                self.wfile.write(audio)
                print(f"Sent {len(audio)} bytes of audio data")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                error_message = f"Internal Server Error: {e}"
                self.wfile.write(error_message.encode())
                print(f"Error: {e}")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

if __name__ == "__main__":
    ip = get_local_ip()
    port = 8000
    server = HTTPServer(('', port), AudioServerHandler)
    print(f"Starting server at http://{ip}:{port}/cgi-bin/mugsworth.cgi")
    server.serve_forever()
