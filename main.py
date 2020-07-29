from flask import Flask, request, redirect, render_template, make_response, session, url_for
from flask_bootstrap import Bootstrap
import serial, time, json

from app import create_app

from datetime import datetime, date
from app.firestore_service import get_today_measurements, get_date, validate_deviation, post_data, get_table_values, values_list
from app.models import JsonFiles

app = create_app()

jsonFiles = JsonFiles()

	
#Inicializamos el puerto de serie a 9600 baud
#Usar linea de abajo para linux



arduino = serial.Serial('/dev/ttyUSB1', 9600)



#Usar linea de abajo para Windows
#arduino = serial.Serial('COM4',9600)




@app.route('/')
def index():
  response = make_response(redirect('/Home'))
  return response

@app.route('/Home', methods= ['GET', 'POST'])
def Home():
  measurements = get_today_measurements()
  measurements = measurements[-6:]
  today = get_date()

  jsonA = {
    'Voltage' : 0.00,
    'Current_L1': 0.00,
    'Current_L2': 0.00,
    'Short_Circuit': False,
    'measurements': measurements,
  }

  context = {
    'Voltage' : jsonA['Voltage'],
    'Current_L1': jsonA['Current_L1'],
    'Current_L2': jsonA['Current_L2'],
    'Short_Circuit': jsonA['Short_Circuit'],
    'measurements': measurements[::-1],
    'today': today,

    }

  if request.method == 'POST':
    data = json.dumps(request.form)
    data = (data + '\n')
    arduino.write((data).encode())
    
  return make_response(render_template('Home.html',**context))




@app.route('/Data')
def Data():

  get_arduino_data()
    
  response = app.response_class(
        response=json.dumps(jsonFiles.currentFile),
        status=200,
        mimetype='application/json'
    )
  return response





@app.route('/Database', methods= ['GET','POST'])
def Database():

  if request.method == 'POST':
    data = json.dumps(request.form)
    data = json.loads(data)
    date_received = date.fromisoformat(data['Date'])
    date_received = date_received.strftime("%d-%m-%Y")

    measurements = get_today_measurements(date_received= date_received)
    table_values = get_table_values(date_received= date_received)


  else:
    measurements = get_today_measurements()
    table_values = get_table_values()


  Voltage_list, Current_L1_list, Current_L2_list, Short_Circuit_Counter, measurement_list = values_list(measurements= measurements)


  

  context = {
    'measurements': measurements,
    'Voltage_list': Voltage_list,
    'Current_L1_list': Current_L1_list,
    'Current_L2_list': Current_L2_list,
    'measurement_list': measurement_list,
    **table_values
  }
  return render_template('Database.html',**context)






#Funcion donde se recibe la informacion de arduino
def SerialEvent():
  rawString = arduino.readline()
  rawString = rawString.decode('utf-8')
  jsonFile = json.loads(rawString) 
  return jsonFile


def get_arduino_data():
  
  if (arduino.inWaiting()>0):

    #Se obtienen los valores desde el arduino
    jsonFiles.currentFile = SerialEvent()
    print('Current Data ', jsonFiles.currentFile)

#Si ya han habido mediciones, se valida que la medicion no sea igual para no sobrecargar la base de datos
    if jsonFiles.previousFile != None: 
      validate_deviation(current_data= jsonFiles.currentFile, old_data= jsonFiles.previousFile)
      
    else: #En caso de ser la primera medicion, se publica en base de datos
      print("Posting with no data beforehand")
      post_data(jsonFiles.currentFile)
      
    jsonFiles.previousFile = jsonFiles.currentFile
