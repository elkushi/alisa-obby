import http.server, socketserver, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
class H(http.server.SimpleHTTPRequestHandler):
    def guess_type(self, path):
        t = super().guess_type(path)
        if isinstance(t, tuple): t = t[0]
        return "text/html; charset=utf-8" if t == "text/html" else t
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
print("serving on 8731", flush=True)
socketserver.TCPServer(("127.0.0.1", 8731), H).serve_forever()
