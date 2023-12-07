import tkinter 
from tkinter import *
import tkinter.font as font
import time
import threading
import board
import digitalio
import adafruit_max31856
import adafruit_max31865
from datetime import datetime
import datetime
from PIL import ImageTk, Image
import RPi.GPIO as GPIO

ampel_green_pin = 16
ampel_red_pin = 21
ampel_yellow_pin = 20
speed_control_pin = 26
solder_stop_pin = 13
fan_control_pin = 23
buzzer_pin = 22



#Ausgänge schalten
GPIO.setmode(GPIO.BCM)
#Setup der GPIOs
GPIO.setup(17,GPIO.OUT)
GPIO.setup(ampel_green_pin,GPIO.OUT) #ampel grün
GPIO.setup(buzzer_pin,GPIO.OUT)
GPIO.setup(speed_control_pin,GPIO.OUT) #geschwindigkeit
GPIO.setup(solder_stop_pin,GPIO.OUT) #lichttaster lötrahmen
GPIO.setup(6,GPIO.IN) #temperatursensor 2?
#Grüne Ampel einschalten
GPIO.output(ampel_green_pin,GPIO.HIGH)
#Lüfter einschalten
GPIO.output(speed_control_pin,GPIO.HIGH)
#Rahmensperre einschalten 
GPIO.output(solder_stop_pin,GPIO.HIGH)


# Create sensor object, communicating over the board's default SPI bus
spi = board.SPI()

# allocate a CS pin and set the direction
cs1 = digitalio.DigitalInOut(board.D5)
cs1.direction = digitalio.Direction.OUTPUT

cs2= digitalio.DigitalInOut(board.D21)
cs2.direction = digitalio.Direction.OUTPUT

cs3 = digitalio.DigitalInOut(board.D20)
cs3.direction = digitalio.Direction.OUTPUT

# create a thermocouple object with the above
sensor1 = adafruit_max31856.MAX31856(spi, cs1, )  #fehlen da Werte???
sensor2 = adafruit_max31856.MAX31856(spi, cs2)
sensor3 = adafruit_max31865.MAX31865(spi, cs3, wires=4)

#Funktion zum Updaten des Speed Labels
def spd_update_Label():
    #Daten aus der TEMP Datei holen
    with open("/home/pi/Desktop/TEMP.txt","r") as f:
        last_line = f.readLines()[-1]
    f.close()
    #Label updaten
    lblspd.configure(text=str(round(float(lastline),1)) + "m/min")
    #Nach 1Sekunde erneut ausführen
    lblspd.after(1000,spd_update_Label)

#Funktion um die Daten in die CSV Datei zu schreiben
def write_to_csv():
    while True:
        #Daten aus TEMP Datei holen
        with open("/home/pi/Desktop/TEMP.txt", "r") as f:
            last_line = f.readLines()[-1]
        f.close()
        #Aktuelle Zeit und Datum holen
        now = datetime.datetime.today()
        #"Punkt" im String mit "Beistrich" austauschen
        replacesensor1 = str(round(sensor1.temperature)).replace(".",",")
        replacesensor2 = str(round(sensor2.temperature)).replace(".",",")
        replacesensor3 = str(round(sensor3.temperature)).replace(".",",")
       
        # Daten in CSV Datei schreiben
        CSVDatei = open("/home/pi/Desktop/Daten.csv", "a")
        CSVDatei.write(str(replacesensor1)  + ";"
                    + str(replacesensor2)   +";"
                    + str(replacesensor3) + ";"
                    + str(round(float(lastline),2)) + "m/min" + ";"
                    + now.strftime("%H:%M:%S") + ";"
                    + time.strftime("%d-%m-%Y"))
        CSVDatei.write("\n")
        CSVDatei.close()
        time.sleep(5)

#Funktion zum Updaten der Termperatur Labels    
def temp_update_Label():
    #Label Text updaten
    lbltmp1.configure(text=str(round(sensor1.temperature)) + "°C")
    lbltmp2.configure(text=str(round(sensor2.temperature)) + "°C")
    lbltmp3.configure(text=str(round(sensor3.temperature)) + "°C")
    #Nach 1Sekunde erneut ausführen
    lbltmp1.after(1000,temp_update_Label)

#Funktion Max Speed und TEMP
def thresholdtempspeed():
    while True:
        with open("/home/pi/Desktop/TEMP.txt", "r") as f:
            last_line = f.readLines()[-1]
        f.close()
        file=open("/home/pi/Desktop/TEMP.txt","r")
        strspeed = file.readline()
        floatspeed= float(strspeed)
        file.close()
        filecsv = open("/home/pi/Desktop/Daten.csv", "a")
        TEMP1 = round(sensor1.temperature)
        TEMP2 = round(sensor2.temperature)
        TEMP3 = round(sensor3.temperature)
        now = datetime.datetime.now()

        if floatspeed > float(maxspeed):
            Error.append(now.strftime("%H:%M:%S"))
            lblausgabe.configure(text= str(Error[0]) +": Die Geschwindigkeit ist zu Hoch !!!")
            filecsv.write(str(TEMP1)  + ";"
                    + str(TEMP2)   +";"
                    + str(temp_update_Label) + ";"
                    + str(round(float(last_line),2)) + "m/min" + ";"
                    + now.strftime("%H:%M:%S") + ";"
                    + time.strftime("%d-%m-%Y") + ";"
                    + "Die Geschwindigkeit ist zu Hoch !!!")
            #Rote Ampel ein, Buzzer ein und Grüne Ampel Aus 
            GPIO.output(17,GPIO.HIGH)
            GPIO.output(27,GPIO.LOW)
            GPIO.output(buzzer_pin,GPIO.HIGH)
            if GPIO.input(6) == 0:
                time.sleep(.5)
                GPIO.output(solder_stop_pin,GPIO.LOW)
            
        if floatspeed < float(minspeed):
            Error.append(now.strftime("%H:%M:%S"))
            lblausgabe.configure(text= str(Error[0]) +": Die Geschwindigkeit ist zu Niedrig !!!")
            filecsv.write(str(TEMP1)  + ";"
                    + str(TEMP2)   +";"
                    + str(temp_update_Label) + ";"
                    + str(round(float(lastline),2)) + "m/min" + ";"
                    + now.strftime("%H:%M:%S") + ";"
                    + time.strftime("%d-%m-%Y") + ";"
                    + "Die Geschwindigkeit ist zu Hoch !!!")
            #Rote Ampel ein, Buzzer ein und Grüne Ampel Aus 
            GPIO.output(17,GPIO.HIGH)
            GPIO.output(27,GPIO.LOW)
            GPIO.output(buzzer_pin,GPIO.HIGH)
            if GPIO.input(6) == 0:
                time.sleep(.5)
                GPIO.output(solder_stop_pin,GPIO.LOW)
        
        if int(TEMP1) > int(maxtemp1):
            Error.append(now.strftime("%H:%M:%S"))
            lblausgabe.configure(text=str(Error[0]) +": Die Temperatur von Sensor 1 ist zu Hoch !!!")
            filecsv.write(str(TEMP1)  + ";"
                    + str(TEMP2)   +";"
                    + str(TEMP3) + ";"
                    + str(round(float(lastline),2)) + "m/min" + ";"
                    + now.strftime("%H:%M:%S") + ";"
                    + time.strftime("%d-%m-%Y") + ";"
                    + "Die Temperatur von Sensor 1 ist zu Hoch !!!")
            #Rote Ampel ein, Buzzer ein und Grüne Ampel Aus 
            GPIO.output(17,GPIO.HIGH)
            GPIO.output(27,GPIO.LOW)
            GPIO.output(buzzer_pin,GPIO.HIGH)
            if GPIO.input(6) == 0:
                time.sleep(.5)
                GPIO.output(solder_stop_pin,GPIO.LOW)
        if int(TEMP1) < int(mintemp1):
            Error.append(now.strftime("%H:%M:%S"))
            lblausgabe.configure(text=str(Error[0]) +": Die Temperatur von Sensor 1 ist zu Niedrig !!!")
            filecsv.write(str(TEMP1)  + ";"
                    + str(TEMP2)   +";"
                    + str(TEMP3) + ";"
                    + str(round(float(lastline),2)) + "m/min" + ";"
                    + now.strftime("%H:%M:%S") + ";"
                    + time.strftime("%d-%m-%Y") + ";"
                    + "Die Temperatur von Sensor 1 ist zu Hoch !!!")
            #Rote Ampel ein, Buzzer ein und Grüne Ampel Aus 
            GPIO.output(17,GPIO.HIGH)
            GPIO.output(27,GPIO.LOW)
            GPIO.output(buzzer_pin,GPIO.HIGH)
            if GPIO.input(6) == 0:
                time.sleep(.5)
                GPIO.output(solder_stop_pin,GPIO.LOW)
            
        if int(TEMP2) > int(maxtemp2):
            Error.append(now.strftime("%H:%M:%S"))
            lblausgabe.configure(text=str(Error[0])+": Die Temperatur von Sensor 2 ist zu Hoch !!!")
            filecsv.write(str(TEMP1)  + ";"
                    + str(TEMP2)   +";"
                    + str(TEMP3) + ";"
                    + str(round(float(lastline),2)) + "m/min" + ";"
                    + now.strftime("%H:%M:%S") + ";"
                    + time.strftime("%d-%m-%Y") + ";"
                    + "Die Temperatur von Sensor 2 ist zu Hoch !!!")
            #Rote Ampel ein, Buzzer ein und Grüne Ampel Aus 
            GPIO.output(17,GPIO.HIGH)
            GPIO.output(27,GPIO.LOW)
            GPIO.output(buzzer_pin,GPIO.HIGH)
            if GPIO.input(6) == 0:
                time.sleep(.5)
                GPIO.output(solder_stop_pin,GPIO.LOW)

        if int(TEMP2) < int(mintemp2):
            Error.append(now.strftime("%H:%M:%S"))
            lblausgabe.configure(text=str(Error[0])+": Die Temperatur von Sensor 2 ist zu Niedrig !!!")
            filecsv.write(str(TEMP1)  + ";"
                    + str(TEMP2)   +";"
                    + str(TEMP3) + ";"
                    + str(round(float(lastline),2)) + "m/min" + ";"
                    + now.strftime("%H:%M:%S") + ";"
                    + time.strftime("%d-%m-%Y") + ";"
                    + "Die Temperatur von Sensor 2 ist zu Hoch !!!")    
            #Rote Ampel ein, Buzzer ein und Grüne Ampel Aus 
            GPIO.output(17,GPIO.HIGH)
            GPIO.output(27,GPIO.LOW)
            GPIO.output(buzzer_pin, GPIO.HIGH)
            if GPIO.input(6) == 0:
                time.sleep(.5)
                GPIO.output(solder_stop_pin,GPIO.LOW)
        
        if int(TEMP3) >int(maxtemp3):
            Error.append(now.strftime("%H:%M:%S"))
            lblausgabe.configure(text=str(Error[0])+": Die Temperatur von Sensor 3 ist zu Hoch !!!")
            filecsv.write(str(TEMP1)  + ";"
                    + str(TEMP2)   +";"
                    + str(TEMP3) + ";"
                    + str(round(float(lastline),2)) + "m/min" + ";"
                    + now.strftime("%H:%M:%S") + ";"
                    + time.strftime("%d-%m-%Y") + ";"
                    + "Die Temperatur von Sensor 1 ist zu Hoch !!!")
            #Rote Ampel ein, Buzzer ein und Grüne Ampel Aus 
            GPIO.output(17,GPIO.HIGH)
            GPIO.output(27,GPIO.LOW)
            GPIO.output(buzzer_pin,GPIO.HIGH)
            if GPIO.input(6) == 0:
                time.sleep(.5)
                GPIO.output(solder_stop_pin,GPIO.LOW)
            
        if int(TEMP3) <int(mintemp3):
            Error.append(now.strftime("%H:%M:%S"))
            lblausgabe.configure(text=str(Error[0])+": Die Temperatur von Sensor 3 ist zu Niedrig !!!")
            filecsv.write(str(TEMP1)  + ";"
                    + str(TEMP2)   +";"
                    + str(TEMP3) + ";"
                    + str(round(float(lastline),2)) + "m/min" + ";"
                    + now.strftime("%H:%M:%S") + ";"
                    + time.strftime("%d-%m-%Y") + ";"
                    + "Die Temperatur von Sensor 1 ist zu Hoch !!!")
            #Rote Ampel ein, Buzzer ein und Grüne Ampel Aus 
            GPIO.output(17,GPIO.HIGH)
            GPIO.output(27,GPIO.LOW)
            GPIO.output(buzzer_pin,GPIO.HIGH)
            if GPIO.input(6) == 0:
                time.sleep(.5)
                GPIO.output(solder_stop_pin,GPIO.LOW)
            
#Fehler zurücksetzen
def Error_acknowledge():

    #nur wenn fehler bereits beseitigt wurde!!!

    Error.clear()
    lblausgabe.configure(text="")
    #Rote und Buzzer rücksetzten und Grüne Ampel einschalten
    GPIO.output(17,GPIO.LOW)
    GPIO.output(27,GPIO.HIGH)
    GPIO.output(buzzer_pin,GPIO.LOW)
    GPIO.output(solder_stop_pin,GPIO.HIGH)
    
#Array für die Startwerte
Error = []
mintemp1 = 100
mintemp2 = 100
mintemp3 = 100
minspeed = 1

maxtemp1 = 300
maxtemp2 = 300
maxtemp3 = 300
maxspeed = 2



#TopLevel Einstellungen erstellen
def setting():

    def stopset():
        Top.destroy()
        file = open("/home/pi/Desktop/settings.txt","w")
        file.write(
            str(mintemp1) + ";" +
            str(mintemp2) + ";" +
            str(mintemp3) + ";" +
            str(minspeed) + ";" +
            str(maxtemp1) + ";" +
            str(maxtemp2) + ";" + 
            str(maxtemp3) + ";" + 
            str(maxspeed) + ";" 
        )
        lblausgabe.configure(text="Einstellungen wurden gespeichert (;")

    global mintemp1
    global mintemp2
    global mintemp3
    global minspeed

    global maxtemp1
    global maxtemp2
    global maxtemp3
    global maxspeed

    settings = open("/home/pi/Desktop/settings.txt","r")
    daten = settings.readlines()
    spldaten = str(daten).split(";")


    mintemp1 = int(spldaten[0].replace("['",""))
    mintemp2 = int(spldaten[1])
    mintemp3 = int(spldaten[2])
    minspeed = float(spldaten[3])

    maxtemp1 = int(spldaten[4])
    maxtemp2 = int(spldaten[5])
    maxtemp3 = int(spldaten[6])
    maxspeed = float(spldaten[7].replace("']",""))

    

    settings.close()

    #Font für die Lables
    top = font.Font(size=18,)

    Top = Toplevel(Window)
    Top.geometry("700x300")
    Top.title("Einstellungen")
    Top.configure(bg="#b8bdc3")
    Top.attributes("-fullscreen",True)

    def mintemp1plus():
        global mintemp1
        if maxtemp1 < mintemp1 + 10:
            pass
        else:
            mintemp1 = mintemp1+5
            lbltemp1.configure(text=mintemp1)

    def mintemp1minus():
        global mintemp1
        mintemp1 = mintemp1 -5
        lbltemp1.configure(text=mintemp1)

    def mintemp2plus():
        global mintemp2
        if maxtemp2 < mintemp2 + 10:
            pass
        else:
            mintemp2 = mintemp2+5
            lbltemp2.configure(text=mintemp2)

    def mintemp2minus():
        global mintemp2
        mintemp2 = mintemp2 -5
        lbltemp2.configure(text=mintemp2)

    def mintemp3plus():
        global mintemp3
        if maxtemp3 < mintemp3 +10:
            pass
        else:
            mintemp3 = mintemp3+5
            lbltemp3.configure(text=mintemp3)

    def mintemp3minus():
        global mintemp3
        mintemp3 = mintemp3 -5
        lbltemp3.configure(text=mintemp3)

    def minspeedplus():
        global minspeed
        if maxspeed < minspeed + 0.1:
            pass
        else:
            minspeed = round(minspeed+0.1,1)
            lbltemp4.configure(text=minspeed)

    def minspeedminus():
        global minspeed
        minspeed = round(minspeed - 0.1,1)
        lbltemp4.configure(text=minspeed)

#Maximale Temperatur

    def maxtemp1plus():
        global maxtemp1
        maxtemp1 = maxtemp1+5
        lbltemp10.configure(text=maxtemp1)

    
    def maxtemp1minus():
        global maxtemp1
        if mintemp1 + 10 >maxtemp1:
            pass
        else:
            maxtemp1 = maxtemp1 -5
            lbltemp10.configure(text=maxtemp1)

    def maxtemp2plus():
        global maxtemp2
        maxtemp2 = maxtemp2+5
        lbltemp20.configure(text=maxtemp2)

    def maxtemp2minus():
        global maxtemp2
        if mintemp2 +10 >maxtemp2:
            pass
        else:
            maxtemp2 = maxtemp2 -5
            lbltemp20.configure(text=maxtemp2)

    def maxtemp3plus():
        global maxtemp3
        maxtemp3 = maxtemp3+5
        lbltemp30.configure(text=maxtemp3)

    def maxtemp3minus():
        global maxtemp3
        if mintemp3 +10> maxtemp3:
            pass
        else:
            maxtemp3 = maxtemp3 -5
            lbltemp30.configure(text=maxtemp3)

    def maxspeedplus():
        global maxspeed
        maxspeed = round(maxspeed+0.1,1)
        lbltemp40.configure(text=maxspeed)

    def maxspeedminus():
        global maxspeed
        if minspeed + 0.2 >maxspeed:
            pass
        else:
            maxspeed = round(maxspeed- 0.1,1)
            lbltemp40.configure(text=maxspeed)
    

    #Beenden Button (Development)
    lblquit = Button(Top,text="Speichern",state="active",fg="#b90246",command=stopset,font=("Arial",20),image=saveimg_Tk)
    lblquit.grid(row=0,column=7,sticky="NSEW")
    
    #Beschriftungs Spalte Sensor
    lblname1= Label(Top,text="Sensor",bg="#b8bdc3",fg="#b90246",font=("Lato",30))
    lblname1.grid(row=0,column=0,sticky="nsew")

    #Beschriftungs Spalte Minimum
    lblname2= Label(Top,text="Minimum",bg="#b8bdc3",fg="#b90246",font=("Lato",30))
    lblname2.grid(row=0,column=2,sticky="nsew")

    #Beschriftungs Spalte Maximum
    lblname3= Label(Top,text="Maximum",bg="#b8bdc3",fg="#b90246",font=("Lato",30))
    lblname3.grid(row=0,column=6,sticky="nsew")

    #TEMP1 Text
    lbltemp1text = Label(Top,text="TEMP1",bg="#b8bdc3",fg="#b90246",font=("Lato",30))
    lbltemp1text.grid(row=1,column=0,sticky="nsew")
   

    #TEMP2 Text
    lbltemp2text = Label(Top,text="TEMP2",bg="#b8bdc3",fg="#b90246",font=("Lato",30))
    lbltemp2text.grid(row=2,column=0,sticky="nsew")
  

    #TEMP3 Text
    lbltemp3text = Label(Top,text="TEMP3",bg="#b8bdc3",fg="#b90246",font=("Lato",30))
    lbltemp3text.grid(row=3,column=0,sticky="nsew")
  

    #Speed Text
    lblspeedtext = Label(Top,text="Speed",bg="#b8bdc3",fg="#b90246",font=("Lato",30))
    lblspeedtext.grid(row=4,column=0,sticky="nsew")
   

    #Button Temp1 Minus
    btnminustemp1 = Button(Top,text="-",state="active",fg="#b90246",command=mintemp1minus,image=minusimg_Tk)
    btnminustemp1.grid(row=1,column=1,sticky="nsew")

    #Button Temp2 Minus
    btnminustemp2 = Button(Top,text="-",state="active",fg="#b90246",command=mintemp2minus,image=minusimg_Tk)
    btnminustemp2.grid(row=2,column=1,sticky="nsew")

    #Button Temp3 Minus
    btnminustemp3 = Button(Top,text="-",state="active",fg="#b90246",command=mintemp3minus,image=minusimg_Tk)
    btnminustemp3.grid(row=3,column=1,sticky="nsew")
    
    #Button Speed Minus
    btnminustemp4 = Button(Top,text="-",state="active",fg="#b90246",command=minspeedminus,image=minusimg_Tk)
    btnminustemp4.grid(row=4,column=1,sticky="nsew")

    #Label Temp 1 
    lbltemp1 = Label(Top,text=mintemp1,bg="#b8bdc3",fg="#b90246",font=("Lato",30))
    lbltemp1.grid(row=1,column=2,sticky="nsew")
    
    
    #Label Temp 2
    lbltemp2 = Label(Top,text=mintemp2,bg="#b8bdc3",fg="#b90246",font=("Lato",25))
    lbltemp2.grid(row=2,column=2,sticky="nsew")
    

    #Label Temp 3 
    lbltemp3 = Label(Top,text=mintemp3,bg="#b8bdc3",fg="#b90246",font=("Lato",25))
    lbltemp3.grid(row=3,column=2,sticky="nsew")
    

    #Label Speed
    lbltemp4 = Label(Top,text=minspeed,bg="#b8bdc3",fg="#b90246",font=("Lato",25))
    lbltemp4.grid(row=4,column=2,sticky="nsew")
    

    #Button Temp 1 Plus
    btnplustemp1 = Button(Top,image=plusimg_Tk,text="+",state="active",fg="#b90246",command=mintemp1plus)
    btnplustemp1.grid(row=1,column=3,sticky="nsew")

    #Button Temp 2 Plus
    btnplustemp2 = Button(Top,text="+",state="active",fg="#b90246",command=mintemp2plus,image=plusimg_Tk)
    btnplustemp2.grid(row=2,column=3,sticky="nsew")
    
    #Button Temp 3 Plus
    btnplustemp3 = Button(Top,text="+",state="active",fg="#b90246",command=mintemp3plus,image=plusimg_Tk)
    btnplustemp3.grid(row=3,column=3,sticky="nsew")
    
    #Button Speed Plus
    btnplustemp4 = Button(Top,text="+",state="active",fg="#b90246",command=minspeedplus,image=plusimg_Tk)
    btnplustemp4.grid(row=4,column=3,sticky="nsew")


    #Zweite "Spalte" für die Maximalen Werte


    #Button Temp1 Minus
    btnminustemp10 = Button(Top,text="-",state="active",fg="#b90246",command=maxtemp1minus,image=minusimg_Tk)
    btnminustemp10.grid(row=1,column=5,sticky="nsew")

    #Button Temp2 Minus
    btnminustemp20 = Button(Top,text="-",state="active",fg="#b90246",command=maxtemp2minus,image=minusimg_Tk)
    btnminustemp20.grid(row=2,column=5,sticky="nsew")

    #Button Temp3 Minus
    btnminustemp30 = Button(Top,text="-",state="active",fg="#b90246",command=maxtemp3minus,image=minusimg_Tk)
    btnminustemp30.grid(row=3,column=5,sticky="nsew")
    
    #Button Speed Minus
    btnminustemp40 = Button(Top,text="-",state="active",fg="#b90246",command=maxspeedminus,image=minusimg_Tk)
    btnminustemp40.grid(row=4,column=5,sticky="nsew")

    #Label Temp 1 
    lbltemp10 = Label(Top,text=maxtemp1,bg="#b8bdc3",fg="#b90246",font=("Lato",25))
    lbltemp10.grid(row=1,column=6,sticky="nsew")

    
    #Label Temp 2
    lbltemp20 = Label(Top,text=maxtemp2,bg="#b8bdc3",fg="#b90246",font=("Lato",25))
    lbltemp20.grid(row=2,column=6,sticky="nsew")
    

    #Label Temp 3 
    lbltemp30 = Label(Top,text=maxtemp3,bg="#b8bdc3",fg="#b90246",font=("Lato",25))
    lbltemp30.grid(row=3,column=6,sticky="nsew")
   

    #Label Speed
    lbltemp40 = Label(Top,text=maxspeed,bg="#b8bdc3",fg="#b90246",font=("Lato",25))
    lbltemp40.grid(row=4,column=6,sticky="nsew")
    

    #Button Temp 1 Plus
    btnplustemp10 = Button(Top,text="+",state="active",fg="#b90246",command=maxtemp1plus,image=plusimg_Tk)
    btnplustemp10.grid(row=1,column=7,sticky="nsew")

    #Button Temp 2 Plus
    btnplustemp20 = Button(Top,text="+",state="active",fg="#b90246",command=maxtemp2plus,image=plusimg_Tk)
    btnplustemp20.grid(row=2,column=7,sticky="nsew")
    
    #Button Temp 3 Plus
    btnplustemp30 = Button(Top,text="+",state="active",fg="#b90246",command=maxtemp3plus,image=plusimg_Tk)
    btnplustemp30.grid(row=3,column=7,sticky="nsew")
    
    #Button Speed Plus
    btnplustemp40 = Button(Top,text="+",state="active",fg="#b90246",command=maxspeedplus,image=plusimg_Tk)
    btnplustemp40.grid(row=4,column=7,sticky="nsew")
    

    #Resizeable GUI
    Grid.columnconfigure(Top,0,weight=1)
    Grid.columnconfigure(Top,1,weight=1)
    Grid.columnconfigure(Top,2,weight=1)
    Grid.columnconfigure(Top,3,weight=1)
    Grid.columnconfigure(Top,4,weight=1)
    Grid.columnconfigure(Top,5,weight=1)
    Grid.columnconfigure(Top,6,weight=1)
    Grid.columnconfigure(Top,7,weight=1)

    Grid.rowconfigure(Top,0,minsize=50,weight=1)
    Grid.rowconfigure(Top,1,minsize=50,weight=1)
    Grid.rowconfigure(Top,2,minsize=50,weight=1)
    Grid.rowconfigure(Top,3,minsize=50,weight=1)
    Grid.rowconfigure(Top,4,minsize=50,weight=1)

    Top.mainloop



#mainwindow
Window = Tk()   
Window.geometry("500x500")
Window.title("Lötwellen Messung")
Window.configure(bg="#b8bdc3")
Window.attributes("-fullscreen",True)

#Lable 1. Temperatur Sensor
lblbesch1 = Label(Window,text="Calrod",bg="#b8bdc3",fg="#b90246",font=("Lato",40))
lblbesch1.grid(row=0,column=0,sticky="nsew")
lbltmp1 = Label(Window,text = "0",bg="#b8bdc3",fg="#b90246",font=("Lato",40))
lbltmp1.grid(row = 1, column=0, sticky="nsew")


#Lable 2. Temperatur Sensor
lblbesch2 = Label(Window,text="Heißluft",bg="#b8bdc3",fg="#b90246",font=("Lato",40))
lblbesch2.grid(row=0,column=1,sticky="nsew")
lbltmp2 = Label(Window,text="0",bg="#b8bdc3",fg="#b90246",font=("Lato",40))
lbltmp2.grid(row=1,column=1,sticky="nsew")


#Lable 3. Temperatur Sensor
lblbesch3 = Label(Window,text="Zinn",bg="#b8bdc3",fg="#b90246",font=("Lato",40))
lblbesch3.grid(row=0,column=2,sticky="nsew")
lbltmp3 = Label(Window,text="55°",bg="#b8bdc3",fg="#b90246",font=("Lato",40))
lbltmp3.grid(row=1,column=2,sticky="nsew")

#Geschwindigkeits Lable
#Lable ausgeben
lblspd = Label(Window,text="m/s",bg="#b8bdc3",fg="#b90246",font=("Lato",40))
lblspd.grid(row=2,column=1,sticky="nsew")

quitimg = Image.open("check.png")
quitimg = quitimg.resize((100,100),Image.ANTIALIAS)
quitimg_Tk = ImageTk.PhotoImage(quitimg)

#Button zum Quitiern
btnq = Button(Window,image= quitimg_Tk,text="Quittieren",state="active",fg="#b90246",command=Error_acknowledge)
btnq.grid(row=4,column=1,sticky="nsew",columnspan=3,)

setimg = Image.open("Einstellungen.png")   
setimg = setimg.resize((100,100),Image.ANTIALIAS)
setimg_Tk = ImageTk.PhotoImage(setimg)



#Button Einstellungen
btnsettings = Button(Window,image=setimg_Tk,text="Einstellungen",state="active",fg="#b90246",command=setting)
btnsettings.grid(row=4,column=0,sticky="nsew")

#Text Ausgabe fürs Programm
lblausgabe = Label(Window,text="Hier könnte Ihre Werbung stehn",bg="#b8bdc3",fg="#b90246",font=("Lato",20))
lblausgabe.grid(row = 3,columnspan=3,column=0,sticky="nsew")

#Beenden Button (Development)
lblquit = Button(Window,text="X",state="active",fg="#b90246",bg="red",command=Window.destroy)
lblquit.place(x=1225,y=25)

#Resizeable Spalten und Reihen
Grid.columnconfigure(Window,0,weight=1)
Grid.columnconfigure(Window,1,weight=1)
Grid.columnconfigure(Window,2,weight=1)
#Grid.rowconfigure(Window,0,weight=10)
Grid.rowconfigure(Window,1,weight=10)
Grid.rowconfigure(Window,2,weight=1)
Grid.rowconfigure(Window,3,weight=5)
Grid.rowconfigure(Window,4,weight=5)

plusimg = Image.open("plus.png")
plusimg = plusimg.resize((50,50),Image.ANTIALIAS)    
plusimg_Tk = ImageTk.PhotoImage(plusimg)

minusimg = Image.open("minus.png")
minusimg = minusimg.resize((50,50),Image.ANTIALIAS)
minusimg_Tk = ImageTk.PhotoImage(minusimg)

saveimg = Image.open("diskette.png")
saveimg = saveimg.resize((25,25),Image.ANTIALIAS)
saveimg_Tk = ImageTk.PhotoImage(saveimg)
#Update die Lables
spd_update_Label()
temp_update_Label()

#Alle Funktionen die im Hintergrund laufen müssen
def start():
    t1 = threading.Thread(target=write_to_csv)
    t2 = threading.Thread(target=thresholdtempspeed)

    t1.start()
    t2.start()

#Start aller Threads im Hintergrund
start()
Window.mainloop()


 





