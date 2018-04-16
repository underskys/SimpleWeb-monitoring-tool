from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import SocketServer
import sqlite3
import psutil
import json
import re

connect = sqlite3.connect('stat.db')
db = connect.cursor()

def get_data():
    json_obj = {}
    cpu_import = psutil.cpu_percent(interval=1)
    data = str(psutil.virtual_memory()).replace("=", ":").split(', ')
    json_obj['memory'] = {}
    for param in data:
        key, value = param.strip(')').strip('L').split(':')
        if key == 'percent':
            value = str(value)
        else:
            try:
                value = str(int(value)/(1024*1024))
            except Exception as e:
                print(e)
        json_obj['memory'][key] = value
    json_obj['cpu'] = str(cpu_import)
    json_data = json.dumps(json_obj)
    date = datetime.now()
    try:
        db.execute(("INSERT INTO stats VALUES ('{}','{}'").format(str(date), str(json_data)))
    except Exception as e:
        print(e)
    connect.commit()
    return json_data

html = '''
<!DOCTYPE html>
<html lang="en_US"></html>
<head>
    <meta charset="utf-8">
    <title>CPU/Memory monitoring</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script>
    </script>
</head>
<style>
.taskmanager{
    bottom: 0;
    background-color: rgb(58, 58, 58);
    position: relative;
    transition: all 0.5ms;
}

.taskmanager:hover{
    background-color: rgb(92, 92, 92);
}
.taskmanager span{
    bottom: 0;
    display: inline-block;
    float: left;
    width: 25px;
}
</style>
<body>
    <div class="container-fluid">
            <div class="row">
                <div class="col-md-4">
                    <label>CPU usage: </label><br>
                    <div class="taskmanager" style="width:250px;height:100px" id="_cpu_svg">
                    </div>
                </div>
                <div class="col-md-4">
                    <label>Memory usage (used/cached/free): </label><br>
                    <div style="width:500px;height:100px" id="_mem_svg">
                    </div>
                </div>
                <div class="col-md-4">
                </div>
            </div>
            <div class="row">
                <div class="col-md-3">
                    <span id='cpu'></span>
                </div>
                <div class="col-md-6">
                    <span id='memory'></span>
                </div>
                <div class="col-md-3">
                </div>
            </div>
    </div>
</body>
<script>
    var interval = setInterval(function(){
        $.post(".", function(data, status){
                var json = JSON.parse(data)
                console.log(json)
                $('#_cpu_svg').append('<span style="height:'+Math.round(json.cpu)+'px;background-color:rgb('+(parseInt(json.cpu)+100).valueOf()+', '+(200-(2*parseInt(json.cpu))).valueOf()+', 32);"></span>')
                if ( $('#_cpu_svg > span').length > 10){
                    console.log('more')
                    $('#_cpu_svg span:nth-child(1)').remove()
                }
                $('#cpu').text(json.cpu+'%')
                $('#memory').text(json.memory.used +'Mb /'+ json.memory.cached +'Mb /'+json.memory.free+'Mb')
        })
    }, 1000)
</script>
</html>
'''

class SimpleWeb(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(html)

    def do_POST(self):
        self._set_headers()
        self.wfile.write(get_data())

    def do_HEAD(self):
        self._set_headers()

print("Starting http web monitoring at port 8080")
address = ('', 8080)
httpd = HTTPServer(address, SimpleWeb)
httpd.serve_forever()