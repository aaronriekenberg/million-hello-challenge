import tornado.httpserver
import tornado.ioloop
import tornado.process
import tornado.web
import tornado.netutil

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def main():
    app = tornado.web.Application([(r"/test", MainHandler)])

    # Bind sockets *before* forking
    sockets = tornado.netutil.bind_sockets(8080)
    
    # Fork worker processes
    tornado.process.fork_processes(0) # Forks one process per CPU core
    
    # In each child process, add the sockets to the HTTPServer
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()