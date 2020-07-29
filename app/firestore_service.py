import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime




credential = credentials.ApplicationDefault()

firebase_admin.initialize_app(credential=credential)

db = firestore.client()


def get_today_measurements(date_received = 0):

  if date_received != 0:
    measurements = db.collection(date_received).get()
  else:

    date = get_date()
    measurements = db.collection(date).get()


  return measurements

def get_date():
  now = datetime.now()
  date = now.strftime("%d-%m-%Y")
  return date

def get_hour():
  now = datetime.now()
  hour = now.strftime("%H:%M")
  return hour

    
def validate_deviation(current_data, old_data):

  current_Voltage = current_data['Voltage']
  current_Current_L1 = current_data['Current_L1']
  current_Current_L2 = current_data['Current_L2']
  current_Short_Circuit = current_data['Short_Circuit']
  

  old_Voltage = old_data['Voltage']
  old_Current_L1 = old_data['Current_L1']
  old_Current_L2 = old_data['Current_L2']
  old_Short_Circuit = old_data['Short_Circuit']



  
  if abs(current_Voltage - old_Voltage) >= 0.5 :
    post_data(current_data)

  if abs(current_Current_L1 - old_Current_L1) >= 0.5 :
    post_data(current_data)

  if abs(current_Current_L2 - old_Current_L2) >= 0.5 :
    post_data(current_data)

  if current_Short_Circuit != old_Short_Circuit :
    post_data(current_data)



def post_data(current_data):
  date =  get_date()
  hour = get_hour()
  ref = db.collection(date).document(hour)
  ref.set(current_data)


def values_list(measurements):

  Voltage = [] #Lista de todos los valores de Voltaje
  Current_L1 = [] #Lista de todos los valores de Corriente para Linea 1
  Current_L2 = [] #Lista de todos los valores de Corriente para Linea 2
  Short_Circuit_Counter = 0 #Lista de todas las veces a las que ocurrio un corto
  measurements_list = []

  for measure in measurements: #Se agregan todos los valores a sus listas correspondientes
    
    Voltage.append( measure.to_dict()['Voltage'])
    Current_L1.append( measure.to_dict()['Current_L1'])
    Current_L2.append( measure.to_dict()['Current_L2'])
    if measure.to_dict()['Short_Circuit'] == True:
      Short_Circuit_Counter += 1

    measurements_list.append(measure.id)

  return Voltage, Current_L1, Current_L2, Short_Circuit_Counter, measurements_list





def get_table_values(date_received = 0):
  
  if date_received !=0:
    measurements = get_today_measurements(date_received= date_received)
  #Se Toman las medidas realizadas en todo el dia
  else:
    measurements = get_today_measurements()

  Voltage = [] #Lista de todos los valores de Voltaje
  Current_L1 = [] #Lista de todos los valores de Corriente para Linea 1
  Current_L2 = [] #Lista de todos los valores de Corriente para Linea 2
  Short_Circuit_Counter = 0 #Lista de todas las veces a las que ocurrio un corto
  measurements_list = []
  Voltage, Current_L1, Current_L2, Short_Circuit_Counter, measurements_list = values_list(measurements= measurements)

  #Calculo de los promedio de Voltage, Corriente Linea 1 y 2
  avg_Voltage = sum(Voltage) / len( Voltage )
  avg_Current_L1 = sum(Current_L1) / len( Current_L1 )
  avg_Current_L2 = sum(Current_L2) / len ( Current_L2 )

  values = {  #Se guardan esas variables en un diccionario para empaquetarlas y enviarlas a la interfaz

    'maxVoltage': max(Voltage),
    'minVoltage': min(Voltage),
    'Voltage': avg_Voltage,
    'maxCurrent_L1': max(Current_L1),
    'minCurrent_L1': min(Current_L1),
    'Current_L1': avg_Current_L1,
    'maxCurrent_L2': max(Current_L2),
    'minCurrent_L2': min(Current_L2),
    'Current_L2': avg_Current_L2,
    'Short_Circuit_Counter': Short_Circuit_Counter  
  }

  return values
