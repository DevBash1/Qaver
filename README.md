# PyQaver
[PyQaver](https://pypi.org/project/PyQaver) is a PHP like WebServer for Python.  
It comes with some of **PHP**'s Features

## Installation
Install [PyQaver](https://pypi.org/project/PyQaver) Using **pip** or **pip3**  
**pip**
```bash
pip install PyQaver
```
**pip3**
```bash
pip3 install PyQaver
```
## Usage
[PyQaver](https://pypi.org/project/PyQaver) is easy to use,  
and Does Not Require much Configuration.

index.py
```python
from PyQaver import Server

server = Server()
server.start("localhost",8080)
```
[PyQaver](https://pypi.org/project/PyQaver) on default it is set to only parse Python codes in __.htm__ and __.html__ files.  
Which you can change with the **Accept** Class.  
index.py
```python
from PyQaver import Server,Accepts

accepts = Accepts();
accepts.reset([".html",".js"])

server = Server()
server.start("localhost",8080)
```
This will tell **PyQaver** to parse Python Codes in __.html__ and __.js__ files.

This is an example __.js__ file.  
script.js
```javascript
console.log("Hello From JavaScript");
<?python
print("console.log('Hello From Python')")
?>
```
index.html
```html
<html>
<head>
<title>PyQaver</title>
<script src="script.js"></script>
</head>
<body>
<?python
print("<h1>Hello From PyQaver!</h1>")
?>
</body>
</html>
```
You can also import modules too and access the filesystem.  
Checkout Some cool demos [here](https://github.com/DevBash1/PyQaver-Demos)

## Contribution
**PyQaver** is still new and open to contributions.  
**Happy Coding**
