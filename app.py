from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect  
import time
import random
import math
import configparser as ConfigParser
import serial
import MySQLdb

async_mode = None

app = Flask(__name__)

config = ConfigParser.ConfigParser()
config.read('config.cfg')
myhost = config.get('mysqlDB', 'host')
myuser = config.get('mysqlDB', 'user')
mypasswd = config.get('mysqlDB', 'passwd')
mydb = config.get('mysqlDB', 'db')
print(myhost)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 

ser = serial.Serial("/dev/ttyUSB0")
ser.baudrate = 9600
read_ser = ser.readline()


def background_thread(args):
    print('som tu')
    count = 0
    dataList = []
    dataCounter = 0
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
    print(db)
    while True:
        if args:
          A = dict(args).get('A')
          btnV = dict(args).get('btn_value')
        else:
          A = 1
          btnV = 'null'
          
        btnV = dict(args).get('btn_value')
        print('btnv',btnV)
        print('args', args)  
        socketio.sleep(2)
        dataCounter += 1
        count += 1
        print(float(ser.readline()))
        print('btnV', btnV)
        
        if btnV == 0:
            if len(dataList) > 0:
                datas = str(dataList)
                datas = datas.replace("'","\"")
                print('datas')
                print(datas)
                
                cursor = db.cursor()
                cursor.execute("INSERT INTO final (hodnoty) VALUES ('%s')" % (datas))
                
                db.commit()
                
                file = open("static/files/test.txt", "a+");
                file.write("%s\r\n" %datas);
                file.close()
                
            dataList = []
            dataCounter = 0
        
        elif btnV == 1:
            yValue = float(ser.readline())
            dataDict = {
            "x": dataCounter,
            "y": yValue
            }
            dataList.append(dataDict)
            
            socketio.emit('my_response',
                          {'data': float(ser.readline()), 'count': count}, namespace='/test')
        
    db.close()

@app.route('/')
def index():
    return render_template('indexz.html', async_mode=socketio.async_mode)
    
@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['value']
    ser.write(str(message['value']).encode())
    emit('my_response',
         {'data': message['value'], 'count': session['receive_count']})

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@app.route('/dbdata/<string:num>', methods=['GET', 'POST'])
def dbdata(num):
  db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
  cursor = db.cursor()
  print(num)
  cursor.execute("SELECT hodnoty FROM  final WHERE id=%s", num)
  rv = cursor.fetchone()
  return str(rv[0])

@app.route('/read/<string:num>', methods=['GET', 'POST'])
def readmyfile(num):
    fo = open("static/files/test.txt","r")
    rows = fo.readlines()
    return rows[int(num)-1]

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())

@socketio.on('click_eventStart', namespace='/test')
def db_message(message):   
    session['btn_value'] = 1

@socketio.on('click_eventStop', namespace='/test')
def db_message(message):   
    session['btn_value'] = 0

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
