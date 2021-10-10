from http.server import HTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
from socketserver import ThreadingMixIn
import threading
from urllib import parse
import os
import subprocess
import cgi
import io
import random

ID = 0
GET = {}
POST = {}
FILES = {}
COOKIE = {}
SERVER = {}
accepts = [".html",".htm"]
main = None
PATH = None

def setCOOKIE(cookie):
    global COOKIE

    for key, morsel in cookie.items():
        COOKIE[key] = morsel.value

def setGET(string):
    global GET
    try:
        pairs = string.split("&")
        for each in pairs:
            attr = each.split("=")[0]
            value = each.split("=")[1]
            GET[attr] = value
    except:
        return False

def setPOST(string):
    global POST
    try:
        pairs = string.split("&")
        for each in pairs:
            attr = each.split("=")[0]
            value = each.split("=")[1]
            POST[attr] = value
    except:
        return False

def setFILES(string):
    global FILES
    pairs = string.split("&")
    try:
        for each in pairs:
            attr = each.split("=")[0]
            value = each.split("=")[1]
            FILES[attr] = value
    except:
        return False

def isAccepted(path):
    for ext in accepts:
        if(path.endswith(ext)):
            return True
    return False

def getPath(path):
    if(path.endswith("/")):
        file = path[:-1]
        if(os.path.isfile(file + "index.html")):
            return file + "index.html"
        elif(os.path.isfile(file + "index.py")):
            return file + "index.py"
        else:
            return file + "index.html"
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
    global PATH
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
                global GET
                global POST
                global FILES
                global ID
                
                code = "_GET = {}\n".format(GET)
                code += "_POST = {}\n".format(POST)
                code += "_FILES = {}\n".format(FILES)
                code += "_COOKIE = {}\n".format(COOKIE)
                code += "_SERVER = {}\n".format(SERVER)

                code += text[start+8:end]
                #print(code)
                
                f = open(".qaver{}.temp".format(ID), "w")
                f.write(code)
                f.close()

                proc = subprocess.Popen(['python3', ".qaver{}.temp".format(ID),''], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                run = proc.communicate()[0].decode("utf-8")
                #print(run)
                if(run.startswith("Traceback")):
                    #print(run)
                    text = customError(PATH,run)
                    printError(text)
                else:
                    #print(text)
                    text = text.replace(text[start:end+2],run)
                
                start = 0
                end = 0
                continue
    if os.path.exists(".qaver{}.temp".format(ID)):
        os.remove(".qaver{}.temp".format(ID))
    return text
    
def runPyFile(path):
    f = open(path, "r")
    file = f.read()

    global GET
    global POST
    global FILES
    global ID



    code = "_GET = {}\n".format(GET)
    code += "_POST = {}\n".format(POST)
    code += "_FILES = {}\n".format(FILES)
    code += "_COOKIE = {}\n".format(COOKIE)
    code += "_SERVER = {}\n".format(SERVER)
    
    code += file

    f = open(".qaver{}.temp".format(ID), "w")
    f.write(code)
    f.close()

    proc = subprocess.Popen(['python3', ".qaver{}.temp".format(ID),''], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    run = proc.communicate()[0].decode("utf-8")
    if(run.startswith("Traceback")):
        text = customError(path,run)
        printError(text)
    else:
        text = customError(path,run)
    
    if os.path.exists(".qaver{}.temp".format(ID)):
        os.remove(".qaver{}.temp".format(ID))

    return text

def customError(path,error):
    global ID
    text = error
    text = text.replace(".qaver{}.temp".format(ID),path)
    lineNumber = 5
    lineStart = text.find(" line ")
    if(path.endswith(".py")):
        lineNumber = 5

    if(lineStart != -1):
        lineStart += 6
        lineEnd = text.find(" ",lineStart)
        line = int(text[lineStart:lineEnd].replace(",","").strip())

        if(line > lineNumber):
            text = text.replace(" line {}".format(line)," line {}".format(line-lineNumber))
            
    return text

def getFile(path):
    global PATH
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
                    PATH = path
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
        
        global POST
        global FILES
        global ID
        ID = random.randint(1,100000000)
        FILES = {}
        POST = {}
        COOKIE = {}

        SERVER["HTTP_USER_AGENT"] = self.headers.get("User-Agent")
        SERVER["HTTP_HOST"] = self.headers.get("Host")
        SERVER["HTTP_REFERER"] = self.headers.get("Referer")
        SERVER['REMOTE_ADDR'] = self.client_address[0]
        SERVER['REMOTE_PORT'] = self.client_address[1]
        
        cookies = SimpleCookie(self.headers.get('Cookie'))
        setCOOKIE(cookies)
        
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
        PATH = path

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
        
        POSTS = ""
        FILE = ""
        for field in form.keys():
            field_item = form[field]
            if field_item.filename:
                # The field contains an uploaded file
                file_data = field_item.file.read()
                file_len = len(file_data)
                #print(file_data)

                if(FILE == ""):
                    FILE += field + "=.temp/" + field_item.filename
                else:
                    FILE += "&" + field + "=.temp/" + field_item.filename

                if not os.path.exists(".temp"):
                    os.makedirs(".temp")
                setFILES(FILE)

                #Write Files To Temp Folder
                f = open(".temp/"+field_item.filename,"wb")
                f.write(file_data)
                f.close()

                del file_data
            else:
                # Regular form value

                if(POSTS == ""):
                    POSTS += field + "=" + form[field].value
                else:
                    POSTS += "&" + field + "=" + form[field].value
        setPOST(POSTS)
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

        SERVER["HTTP_USER_AGENT"] = self.headers.get("User-Agent")
        SERVER["HTTP_HOST"] = self.headers.get("Host")
        SERVER["HTTP_REFERER"] = self.headers.get("Referer")
        SERVER['REMOTE_ADDR'] = self.client_address[0]
        SERVER['REMOTE_PORT'] = self.client_address[1]
        
        global PATH
        global POST
        global FILES
        FILES = {}
        POST = {}
        COOKIE = {}

        global ID
        ID = random.randint(1,100000000)

        cookies = SimpleCookie(self.headers.get('Cookie'))
        setCOOKIE(cookies)
        
        parsed_path = parse.urlparse(self.path)
        
        setGET(parsed_path.query)
        
        parsed_path = '{}'.format(parsed_path.path)
        path = getPath(parsed_path)
        PATH = path

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
