#!/usr/bin/python3
from flask import Flask
from math import log as logln
import pymysql
import pymysql.cursors
import logging
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler('rpiHttp.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.CRITICAL)
app = Flask(__name__)
app.logger.addHandler(handler)

@app.route("/",defaults={'day1': 1,'day2':0})
@app.route("/<int:day1>",defaults={'day2':0})
@app.route("/<int:day1>/<int:day2>")
def main(day1,day2): 
    links = "/daysBack/daysForward <br>ie. default is /1/0 for last day, /2/1 for yesterday <br> "
    pretty = sqlToPretty(tempOut(day1,day2))
    return "<html><body>{}{}</body></html>".format(links,pretty)

@app.route("/tempOhms/<int:sample>")
def ohmsIn(sample):
    f = steinhart(sample)
    logMeasure(sample,f) 
    return "Spank-you"

def steinhart(sample):
    average = 1023 / sample - 1
    average = 10000 / average
    stein = average / 10000
    stein = logln(stein)
    stein = stein / 3950.0
    stein = stein + 1.0 / (25.0 + 273.15)
    stein = 1.0 / stein
    stein = stein - 273.15
    f = (9/5.0 * stein) + 32.0
    return f

@app.route("/tempIn/<float:temp>")
def tempIn(temp):
    logMeasure(-1,temp) 
    return "Spank-you"

@app.route("/tempHumidIn/<string:device>/<float:temp>/<float:humid>")
def tempHumidIn(device,temp,humid):
    logMeasures(-1,device,temp,humid) 
    return "Spank-you"

def logMeasures(mO,mD,mF,mH):
## rpi@localhost password:rpi database=freezer table=measurements (measureTime,measurementDegF)
    conn= pymysql.connect(host='localhost',user='rpi',password='rpi',db='freezer',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    a=conn.cursor()
    sql="insert into measurements (measureOhms,measureDegF,measureHumid,measureDevice) values ({},{},{},{})".format(mO,mF,mH,mD);
    a.execute(sql)
    a.execute("commit;")

def logMeasure(mO,mF):
## rpi@localhost password:rpi database=freezer table=measurements (measureTime,measurementDegF)
    conn= pymysql.connect(host='localhost',user='rpi',password='rpi',db='freezer',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    a=conn.cursor()
    sql="insert into measurements (measureOhms,measureDegF) values ({},{})".format(mO,mF);
    #sql="insert into measurements(measureTime,measureDegF) values (sysdate(),{});".format(temp)
    a.execute(sql)
    a.execute("commit;")

@app.route("/purgemeasurements/<float:days>")
def purge(days):
## rpi@localhost password:rpi database=freezer table=measurements (measureTime,measurementDegF)
    conn= pymysql.connect(host='localhost',user='rpi',password='rpi',db='freezer',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    a=conn.cursor()
    sql="delete from measurements where measureTime < DATE_SUB(now(),INTERVAL {} DAY)".format(days);
    a.execute(sql)
    a.execute("commit;")

def tempOut(day1,day2):
## rpi@localhost password:rpi database=freezer table=measurements (measureTime,measurementDegF)
    conn= pymysql.connect(host='localhost',user='rpi',password='rpi',db='freezer',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    a=conn.cursor()
    sql="select * from measurements where measureTime between DATE_SUB(now(), INTERVAL {} DAY) and DATE_SUB(now(), INTERVAL {} DAY)".format(day1,day2)
    cnt = a.execute(sql)
    return a.fetchall()

def sqlToPretty(datar):
    import plotly.plotly as py
    import plotly.offline as offline
    import plotly.graph_objs as go

    dates = [row['measureTime'] for row in datar if row['measureDevice'] == 'therm0']
    dates2 = [row['measureTime'] for row in datar if row['measureDevice']!= 'therm0']
    degs = [row['measureDegF'] for row in datar if row['measureDevice'] == 'therm0']
    degs2 = [row['measureDegF'] for row in datar if row['measureDevice'] != 'therm0']
    hums = [row['measureHumid'] for row in datar if row['measureDevice'] != 'therm0']
    
    trace0 = go.Scatter(
        x = dates,
        y = degs,
        name = 'Freezer dF',
        line = dict(
            color = ('rgb(205, 12, 24)'),
            width = 4),
        connectgaps=True
    )
    trace1 = go.Scatter(
        x = dates2,
        y = degs2,
        name = 'Room dF',
        line = dict(
            color = ('rgb(22, 96, 167)'),
            width = 4,),
        connectgaps=True
    )
    trace2 = go.Scatter(
        x = dates2,
        y = hums,
        name = 'Room Humidity%',
        line = dict(
            color = ('rgb(122, 196, 67)'),
            width = 4,),
        connectgaps=True,
        yaxis='y2'
    )
    data = [trace0, trace1, trace2]
    
    # Edit the layout
    layout = dict(title = 'Casa De Clowtown',
                  hovermode = 'closest',
                  xaxis = dict(title = '2 minutes polling',ticklen=5,zeroline=False,gridwidth=2),
                  yaxis = dict(title = 'Temperature (degrees F)',ticklen=5,gridwidth=2,dtick=5.0,range=[-10,90]),
                  yaxis2=dict(
                              title='Humidity%',
                              titlefont=dict(
                                  color='rgb(148, 103, 189)'
                              ),
                              tickfont=dict(
                                  color='rgb(148, 103, 189)'
                              ),
                              overlaying='y',
                              side='right',
                              ticklen=5,gridwidth=2,dtick=5.0,
                              range=[0,100]
                          ),
                  showlegend=True
                  )
    """
    layout= go.Layout(
        title= 'Casa De Clowtown @Thermistor',
        hovermode= 'closest',
        xaxis= dict(
            title= '2 minutes',
            ticklen= 5,
            zeroline= False,
            gridwidth= 2,
        ),
        yaxis=dict(
            title= 'Temp ºF',
            ticklen= 5,
            gridwidth= 2,
            dtick=5.0,
            range=[-10,90],
        ),
        showlegend= False
    )
    data = [go.Scatter(x=dates,y=degs),go.Scatter(x=dates2,y=degs2),go.Scatter(x=dates2,y=hums)]
    """
    fig = dict(data=data, layout=layout)
    plot = offline.plot(fig,output_type='div')
    return plot

app.debug = True

app.run('0.0.0.0', 80, threaded = True, use_reloader = True, use_debugger = True)
