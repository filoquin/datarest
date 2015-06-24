#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import pymssql
import pydtt
from dicttoxml import dicttoxml
from flask import  Flask, url_for,  json, jsonify, request, Response
from flask.ext.cors import CORS 
from functools import wraps
import decimal
import datetime 
import sys

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

def check_auth(username, password):
    return True
    return username == 'admin' and password == 'secret'

def authenticate():
    message = {'message': "Authenticate."}
    resp = jsonify(message)

    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'

    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        print request
        if not auth: 
            return authenticate()

        elif not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


def return_result_set(result_set):
    if request.headers['Content-Type'] == 'text/plain':
        str= "\n"
        return str.join(result_set)

    elif request.headers['Content-Type'] == 'application/json':
        return json.dumps(result_set, default=decimal_default)


    elif request.headers['Content-Type'] == 'application/xml':
        return dicttoxml(result_set)

    else:
        print result_set
        return json.dumps(result_set,cls=EnhancedJSONEncoder)


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    '''if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d $H:%M:%S.%f')
    	raise TypeError ("Type not serializable")
    '''

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S.%f')
            ARGS = ('year', 'month', 'day', 'hour', 'minute',
                     'second', 'microsecond')
            return {'__type__': 'datetime.datetime',
                    'args': [getattr(obj, a) for a in ARGS]}
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
            ARGS = ('year', 'month', 'day')
            return {'__type__': 'datetime.date',
                    'args': [getattr(obj, a) for a in ARGS]}
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M:%S.%f')
            ARGS = ('hour', 'minute', 'second', 'microsecond')
            return {'__type__': 'datetime.time',
                    'args': [getattr(obj, a) for a in ARGS]}
        elif isinstance(obj, datetime.timedelta):
            return obj.strftime('%j%S%f')
            ARGS = ('days', 'seconds', 'microseconds')
            return {'__type__': 'datetime.timedelta',
                    'args': [getattr(obj, a) for a in ARGS]}
        elif isinstance(obj, decimal.Decimal):
            return str(obj)
        else:
            return super().default(obj)



@app.route('/')
def api_root():
    ret ={'status':'ok'}
    return return_result_set(ret)


'''
''
'' REST 
'' Me permite acceder a RESTSERVEER
'' 
'' 
''
'''

@app.route('/restserver/<parent>/<action>')
def api_rest(parent,action):

    
    transaction = getattr(pydtt, "pydtt.pydtt_"+ parent)('POLICLI','POLICLI', 'PNSA\\meditim', 'riv$%250')
    print transaction

    ret ={'status':'ok'}
    return return_result_set(ret)
    
    return return_result_set(transaction.search())

    return return_result_set(eval("transaction."+action))




'''
''
'' EMPRESAS
'' Me permite acceder a los registros le las empresas
'' /empresas regito de todas las empresas
'' /empresas/search
''
'''

@app.route('/empresas',methods = ['GET', 'POST'])
def api_empresas():
    transaction=pydtt.pydtt_empresas('POLICLI','POLICLI', 'PNSA\\meditim', 'riv$%250')
    return return_result_set(transaction.get_all())

@app.route('/empresas/search')
def api_search_empresas():
    transaction=pydtt.pydtt_empresas('POLICLI','POLICLI', 'PNSA\\meditim', 'riv$%250')
    return return_result_set(transaction.search())

'''
''
'' PACIENTES
'' Me permite acceder a los registros de los pacienes
'' 
'' /pacientes/search
''
'''

@app.route('/pacientes/search')
def api_pacientes():
    transaction=pydtt.pydtt_paciente('POLICLI','POLICLI', 'PNSA\\meditim', 'riv$%250')
    return return_result_set(transaction.search())

@app.route('/pacientes/browse/<hlc>')
def api_pacientes_browse(hlc):
    transaction=pydtt.pydtt_paciente('POLICLI','POLICLI', 'PNSA\\meditim', 'riv$%250')
    return return_result_set(transaction.browse(hlc))

@app.route('/pacientes/hc/browse/<hlc>')
def api_pacientes_hc_browse(hlc):
    transaction=pydtt.pydtt_paciente('POLICLI','POLICLI', 'PNSA\\meditim', 'riv$%250')
    return return_result_set(transaction.browse_hc(hlc))


'''
''
'' ART
'' Me permite acceder a los registros le las ART
'' /art regito de todas las art
'' /art/search
''
'''
@app.route('/art',methods = ['GET', 'POST'])
def api_art():
    
    transaction=pydtt.pydtt_art('POLICLI','POLICLI', 'PNSA\\meditim', 'riv$%250')
    return return_result_set(transaction.get_all())

@app.route('/art/search')
def api_search_art():
    transaction=pydtt.pydtt_art('POLICLI','POLICLI', 'PNSA\\meditim', 'riv$%250')
    return return_result_set(transaction.search())



'''
''
'' HC
'' Ingresos de los pacientes
'' /api_hc_ingresos/tie ingresos desde el time
'' 
''
'''

@app.route('/hc/ingresos/<from_time>')
def api_hc_ingresos(from_time):
    transaction=pydtt.pydtt_hc('POLICLI','POLICLI', 'PNSA\\meditim', 'riv$%250')
    return return_result_set(transaction.get_from_time(from_time))

@app.route('/hc/internados/<from_time>')
def api_hc_internados(from_time):
    transaction=pydtt.pydtt_hc('POLICLI','POLICLI', 'PNSA\\meditim', 'riv$%250')
    return return_result_set(transaction.get_internados_from_time(from_time))


@app.route('/hc/insert_new_data',methods = ['GET', 'POST'])
def api_hc_insert_new(from_time):
    transaction=pydtt.pydtt_hc('POLICLI','PRUEBA_HC', 'PNSA\\meditim', 'riv$%250')
    return return_result_set(transaction.api_hc_insert_new(from_time))


@app.route('/hc/browse/<pac>')
def api_hc_browse(pac):
    transaction=pydtt.pydtt_hc('POLICLI','POLICLI', 'PNSA\\meditim', 'riv$%250')
    return return_result_set(transaction.browse(pac))


@app.route('/laboral/empresas/all',methods = ['GET', 'POST'])
def laboral_empresas_all():
    transaction=pydtt.laboral('POLICLI','laboralsoft', 'PNSA\\meditim', 'riv$%250')
    return return_result_set(transaction.empresas_all())


@app.route('/crud/query',methods = ['GET', 'POST'])
def api_crud():
    transaction=pydtt.pydtt_crud('POLICLI','POLICLI', 'PNSA\\meditim', 'riv$%250')

    return return_result_set(transaction.query())

if __name__ == '__main__':
    app.run(host="10.0.5.41",port=5010)

