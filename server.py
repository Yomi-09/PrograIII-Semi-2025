from http.server import HTTPServer, SimpleHTTPRequestHandler
port = 3000
class miServidor(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path=="/":
            self.path = "/index.html"
            return SimpleHTTPRequestHandler.do_GET(self)
    def do_POST(self):
        longitud = int(self.headers['Content-Length'])
        datos = self.rfile.read(longitud)
        datos = datos.decode("utf-8")
        datos = parse.unquote(datos)
        print(datos)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(datos.encode)("utp")
                
print("Servidor ejecutandose")
server = HTTPServer(("localhost",port),miServidor)
server.serve_forever()
