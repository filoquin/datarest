# -*- encoding: utf-8 -*-
import pymssql
import pydtt
from dicttoxml import dicttoxml
from flask import  Flask, url_for,  json, jsonify, request, Response
from functools import wraps



app = Flask(__name__)

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
        return json.dumps(result_set)

    elif request.headers['Content-Type'] == 'application/xml':
        return dicttoxml(result_set)

    else:
        return json.dumps(result_set)

@app.route('/')
def api_root():
    ret ={'status':'ok'}
    return return_result_set(ret)
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
    transaction=pydtt.pydtt_empresas('host','db','usr','pass')
    return return_result_set(transaction.get_all())

@app.route('/empresas/search')
def api_search_empresas():
    transaction=pydtt.pydtt_empresas('host','db','usr','pass')
    return return_result_set(transaction.search())

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
    
    transaction=pydtt.pydtt_art('host','db','usr','pass')
    return return_result_set(transaction.get_all())

@app.route('/art/search')
def api_search_art():
    transaction=pydtt.pydtt_art('host','db','usr','pass')
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
    transaction=pydtt.pydtt_hc('host','db','usr','pass')
    return return_result_set(transaction.get_from_time(from_time))



if __name__ == '__main__':
    app.run(host="10.0.5.41",port=5010)

