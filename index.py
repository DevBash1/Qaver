from qaver import Server,Accepts

accepts = Accepts();
accepts.reset([".html",".js"])

server = Server()
server.start("localhost",8080)