from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
from urllib import parse
import os
import subprocess
import cgi
import io

query = ""
POSTS = ""
FILES = ""
accepts = [".html",".htm"]
main = None

def isAccepted(path):
    for ext in accepts:
        if(path.endswith(ext)):
            return True
    return False

def getPath(path):
    if(path.endswith("/")):
        return path[:-1] + "index.html"
    else:
        if(path.startswith("/")):
            return path[1:]
        else:
            return path

def printError(string):
    print('\033[93m' + string + '\033[0m')

def is_binary(filename):
    """Return true if the given filename is binary.
    @raise EnvironmentError: if the file does not exist or cannot be accessed.
    @attention: found @ http://bytes.com/topic/python/answers/21222-determine-file-type-binary-text on 6/08/2010
    @author: Trent Mick <TrentM@ActiveState.com>
    @author: Jorge Orpinel <jorge@orpinel.com>"""
    
    try:
        fin = open(filename, 'rb')
    except:
        return False
    try:
        CHUNKSIZE = 1024
        while 1:
            try:
                chunk = fin.read(CHUNKSIZE)
                if '\0' in chunk:
                    return True
                if len(chunk) < CHUNKSIZE:
                    break
            except:
                return False
    finally:
        fin.close()

    return False

def parseFile(string):
    text = string
    parsed = ""
    start = 0
    end = 0;
    stop = False;

    while stop == False:
        headIndex = text.find("<?python")
        if(headIndex == -1):
            stop = True
            break
        else:
            start = headIndex
            footIndex = text.find("?>",start+1)
            if(footIndex == -1):
                stop = True
                break
            else:
                end = footIndex
                global query
                code = """
def _GET(attr):
    query = "{}"
    try:
        pairs = query.split("&")
        for each in pairs:
            if(each.split("=")[0] == attr):
                return each.split("=")[1]
    except:
        return False
    return False

""".format(query)
                code += text[start+8:end]
                
                f = open(".qaver.temp", "w")
                f.write(code)
                f.close()

                proc = subprocess.Popen(['python', '.qaver.temp',''], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                run = proc.communicate()[0].decode("utf-8")
                if(run.startswith("Traceback")):
                    text = text.replace(text[start:end+2],"<p style='background:yellow;border:2px solid red;color:red;padding:15px'>Qaver Error: " + run[run.find(" in ")+3:] + "</p>")
                    printError(run[run.find(" in ")+3:])
                else:
                    text = text.replace(text[start:end+2],run)
                
                start = 0
                end = 0
                continue
    return text
    
def runPyFile(path):
    f = open(path, "r")
    file = f.read()

    global query
    global POSTS
    global FILES

    code = """
def _GET(attr):
    query = "{}"
    try:
        pairs = query.split("&")
        for each in pairs:
            if(each.split("=")[0] == attr):
                return each.split("=")[1]
    except:
        return False
    return False

""".format(query)

    code += """
def _POST(attr):
    query = "{}"
    try:
        pairs = query.split("&")
        for each in pairs:
            if(each.split("=")[0] == attr):
                return each.split("=")[1]
    except:
        return False
    return False

""".format(POSTS)

    code += """
def _FILES(attr):
    query = "{}"
    try:
        pairs = query.split("&")
        for each in pairs:
            if(each.split("=")[0] == attr):
                return each.split("=")[1]
    except:
        return False
    return False

""".format(FILES)
    code += file

    f = open(".qaver.temp", "w")
    f.write(code)
    f.close()

    proc = subprocess.Popen(['python', '.qaver.temp',''], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    run = proc.communicate()[0].decode("utf-8")
    if(run.startswith("Traceback")):
        text = run[run.find(" in ")+3:]
        printError(run[run.find(" in ")+3:])
    else:
        text = run
    return text


def getFile(path):
    os.chdir('.')

    if(path.endswith(".py")):
        return runPyFile(path)
    
    if(os.path.isfile(path)):
        #check if is binary and return without parsing

        if(is_binary(path)):
            f = open(path, "rb")
            return f.read()
        else:
            f = open(path, "r")
            try:
                if(isAccepted(path)):
                    return parseFile(f.read())
                else:
                     return f.read()
            except:
                f = open(path, "rb")
                return f.read()
    else:
        return "";

class GetHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        #global main
        #main = self

        global POSTS
        global FILES
        FILES = ""
        POSTS = ""

        # Parse the form data posted
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': self.headers['Content-Type'],
            }
        )

        out = io.TextIOWrapper(
            self.wfile,
            encoding='utf-8',
            line_buffering=False,
            write_through=True,
        )

        path = getPath('{}'.format(self.path))

        if(os.path.isfile(path)):
            self.send_response(200)
        else:
            self.send_response(404)
            #self.send_error(404)
            return False;
        
        self.send_header("Server","Qaver Server V0.1")
        
        if(path.endswith(".html") or path.endswith(".htm")):
            self.send_header('Content-Type',
                         'text/html; charset=utf-8')
        elif(path.endswith(".py")):
            self.send_header('Content-Type',
                         'text/html; charset=utf-8')
        else:
            self.send_header('Content-Type',
                         'text/plain; charset=utf-8')
        
        self.server_version = "Qaver Server V0.1"
        self.sys_version = ""
        self.protocol_version = ""
               
        self.end_headers()

        #out.write('Client: {}\n'.format(self.client_address))
        #out.write('User-agent: {}\n'.format(
            #self.headers['user-agent']))
        #out.write('Path: {}\n'.format(self.path))
        #out.write('Form data:\n')

        # Echo back information about what was posted in the form
        for field in form.keys():
            field_item = form[field]
            if field_item.filename:
                # The field contains an uploaded file
                file_data = field_item.file.read()
                file_len = len(file_data)
                #print(file_data)

                if(FILES == ""):
                    FILES += field + "=.temp/" + field_item.filename
                else:
                    FILES += "&" + field + "=.temp/" + field_item.filename

                #Write Files To Temp Folder
                f = open(".temp/"+field_item.filename,"wb")
                f.write(file_data)
                f.close()

                del file_data
                #out.write(
                #    '\tUploaded {} as {!r} ({} bytes)\n'.format(
                #       field, field_item.filename, file_len)
                #)
            else:
                # Regular form value
                
                if(POSTS == ""):
                    POSTS += field + "=" + form[field].value
                else:
                    POSTS += "&" + field + "=" + form[field].value

                #out.write('\t{}={}\n'.format(
                #   field, form[field].value))
        
        if(path.endswith(".html") or path.endswith(".htm")):
            f = open(path,"rb");
            out.write(parseFile(f.read().decode("utf-8")))
        elif(path.endswith(".py")):
            code = runPyFile(path)
            out.write(code)
        else:
            f = open(path,"rb");
            try:
                out.write(f.read().decode("utf-8"))
            except:
                out.write("")
                    
        # Disconnect our encoding wrapper from the underlying
        # buffer so that deleting the wrapper doesn't close
        # the socket, which is still being used by the server.
        out.detach()

    def do_GET(self):
        #global main
        #main = self
        
        parsed_path = parse.urlparse(self.path)
        
        global query
        query = '{}'.format(parsed_path.query)
        
        parsed_path = '{}'.format(parsed_path.path)
        path = getPath(parsed_path)

        if(os.path.isfile(path)):
            self.send_response(200)
        else:
            self.send_response(404)
            #self.send_error(404)
        
        if(path.endswith(".html") or path.endswith(".htm")):
            self.send_header('Content-Type',
                         'text/html; charset=utf-8')
        elif(path.endswith(".py")):
            self.send_header('Content-Type',
                         'text/html; charset=utf-8')
        else:
            self.send_header('Content-Type',
                         'text/plain; charset=utf-8')
        
        self.server_version = "Qaver Server V0.1"
        self.sys_version = ""
        self.protocol_version = ""
             
        self.end_headers()
        
        file = getFile(path)
        
        if(is_binary(path)):
            self.wfile.write(file)
        else:
            try:
                self.wfile.write(file.encode('utf-8'));
            except:
                self.wfile.write(file);

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    
class Server:
    address = "localhost";
    port = 8080

    def start(config,address,port):
        server = ThreadedHTTPServer((address, port), GetHandler)
        print('Server Running on Port {}, use <Ctrl-C> to stop'.format(port))
        try:
            server.serve_forever()
        except:
            server.server_close()

class Accepts:
    def add(*array):
        global accepts
        accepts = accepts + array[1]
        
    def reset(*array):
        global accepts
        if(len(array) == 1):
            accepts = [".html",".htm"]
            return False
        accepts = array[1]
