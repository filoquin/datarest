# -*- encoding: utf-8 -*-
import pymssql
from flask import  Flask, url_for,  json, jsonify, request, Response


class pyddt(object):
    condition = ''
    filters ={}
    def __init__(self,url,dbname,username,pwd):

        self.url = url
        self.dbname = dbname
        self.username = username
        self.pwd = pwd

        self.connect_pyddt()

    def connect_pyddt(self):

        #conecto a la DB, as_dict=True para obtener clave alfanumerica
        conn = pymssql.connect(self.url, self.username, self.pwd, self.dbname,0,60,"cp1252")
        self.cursor = conn.cursor(as_dict=True)

    def get_all(self):
        pass

    def set_attr(self,var,value):
        setattr(self, var, value)

    def set_filter(self,value):
        self.filters.append(value)

    def make_conditions(self,conditions):
        condition = []
        op = ' and '
        for parameters in self.active_parameters:
            arg = request.args.get(parameters)
            if arg:
                condition.append("%s = '%s'" % (self.active_parameters[parameters], arg) )

        self.condition = op.join(condition)

    def make_special_conditions(self,conditions):
        condition = []
        op = ' and '
        keys =  self.active_parameters.keys()
        for parameters in keys:
            arg = request.args.get(parameters)
            if arg:

                if(self.active_parameters[parameters]['type']=="like"):
                    condition.append("%s like '%%%s%%'" % (self.active_parameters[parameters]['field'], arg) )
                elif(self.active_parameters[parameters]['type']=="ilike"):
                    arg=arg.replace('*','%');
                    condition.append("upper(%s) like upper('%%%s%%')" % (self.active_parameters[parameters]['field'], arg) )
                elif(self.active_parameters[parameters]['type']=="startby"):
                    condition.append("%s like '%s%%'" % (self.active_parameters[parameters]['field'], arg) )
                elif(self.active_parameters[parameters]['type']=="number"):
                    condition.append("%s =%f" % (self.active_parameters[parameters]['field'], arg) )
                elif(self.active_parameters[parameters]['type']=="gdnu"):
                    dnu=arg[1:]
                    genero=arg[:1]
                    condition.append("NDO =%f" % ( dnu) )
                else : 
                    condition.append("%s = '%s'" % (self.active_parameters[parameters]['field'], arg) )

        self.condition = op.join(condition)




class pydtt_empresas(pyddt):

    active_parameters={'DES':'DES','INS':'INS'}

    def get_all(self):
        self.cursor.execute("select INS, DES,DIR,LOC,CPO,CUI,NGA "
            "from dbo.CLINST "
            "where INS not like 'm%' and ISNUMERIC(INS)=1 and "
            "(convert (INT, INS) > 9000 or (convert (INT, INS) > 5000 and convert (INT, INS) < 6000) ) "
        )

        return self.cursor.fetchall()

    def search(self):
        self.make_conditions(request.args)
        self.cursor.execute("select INS, DES,DIR,LOC,CPO,CUI,NGA "
            "from dbo.CLINST "
            "where INS not like 'm%' and ISNUMERIC(INS)=1 and "
            "(convert (INT, INS) > 9000 or (convert (INT, INS) > 5000 and convert (INT, INS) < 6000) ) "
            "and "  + self.condition
        )
        return self.cursor.fetchall()

class pydtt_art(pyddt):
    active_parameters={'DES':'DES','INS':'INS'}

    def get_all(self):
        self.cursor.execute("select INS, DES,DIR,LOC,CPO,CUI,NGA "
            "from dbo.CLINST "
            "where INS not like 'm%' and ISNUMERIC(INS)=1 and "
            " (convert (INT, INS) > 4300 and convert (INT,INS) < 4999) "
        )

        return self.cursor.fetchall()

    def search(self):

        self.make_conditions(request.args)
        self.cursor.execute("select INS, DES,DIR,LOC,CPO,CUI,NGA "
            "from dbo.CLINST "
            "where INS not like 'm%' and ISNUMERIC(INS)=1 and "
            "( (convert (INT, pac.INS) > 4300 and convert (INT, pac.INS) < 4999) "
            "and DES like '%(cond)s'"  % filters
        )
        return self.cursor.fetchall()

class pydtt_hc(pyddt):
    active_parameters={'nombre':{'field':'NOM','type':'ilike' },'dnu':{'field':'NDO','type':'startby' },'hcl':{'field':'HCL','type':'number' },'pac':{'field':'PAC','type':'number' }}

    def get_from_time(self,start_time):
        self.cursor.execute("select  ORI, PAC , pac.NOM , pac.DIR , pac.LOC, pac.CPO, pac.TEL, convert(varchar, pac.FNA , 111) as FNA, pac.SEX,  pac.NDO, "
            "pac.INS, pac.HCL ,  convert(varchar,FIN, 120) as FIN , l.DES as localidad "
            "from CLIPAC pac "
            "left join CLIHCL hcl on (pac.HCL = hcl.HCL ) "
            "left join CLILOC l on (l.LOC = pac.LOC ) "
            "where ORI='A' "
            "and FIN>= '%s' and ISNUMERIC(pac.INS)=1 and "
            "( (convert (INT, pac.INS) > 4300 and convert (INT, pac.INS) < 4999) ) " % (start_time)
        )

        return self.cursor.fetchall()

    def get_internados_from_time(self,start_time):
        
        self.cursor.execute("select  pac.* "
            "from CLIPAC pac "
            "left join CLIHCL hcl on (pac.HCL = hcl.HCL ) "
            "where ORI='I' "
            "and FIN>= '%s' " % (start_time)
        )

        return self.cursor.fetchall()
    def search(self):
        self.make_special_conditions(request.args)

        self.cursor.execute("select top 100 NOM, NDO , HCL , PAC "
            "from CLIPAC pac "
            "where " + self.condition 
        )
        return self.cursor.fetchall()

    def browse(self,pac):
        self.make_special_conditions(request.args)
        result_set=[]
        self.cursor.execute("select top 1 * "
            "from CLIPAC pac "
            "where " + self.condition 
        )

        for row in self.cursor.fetchall():
            item=row
            self.cursor.execute("select  tipo.DES , preg.LEY_1 , ope.NOM as operador ,ev.* "
                        "from CNSRSP  ev "
                        "join CNSANA  tipo on (ev.ANA=tipo.ANA) "
                        "join CNSPRG preg on (ev.PRG=preg.PRG) "
                        "join SYSOPE ope on (ev.OPE=ope.OPE) "
                        "where ev.PAC=%d" % (row['PAC']))
            item['preguntas']=self.cursor.fetchall()
            result_set.append(item)
        return result_set

    def api_hc_insert_new(self):
        pass
    def get_paciente(self,paciente):
        hcl = self.cursor.execute("select  HCL from CLIHCL where SEX='%s' NDO='%f'"%(paciente['genero'],paciente['dnu'])).fetchone()
        if (hcl is None):
            self.create_hcl(paciente)
        else : 
            return hcl['HCL']
    def create_paciente(self,paciente):
        pass
    def next_geneador(self,codigo):
        pass
        


class laboral(pyddt):

    def empresas_all(self):
        self.cursor.execute("select  razonsocial,  CUIT, domicilio from empresas where activa =1" )
        return self.cursor.fetchall()




class pydtt_paciente(pyddt):
    active_parameters={'nombre':{'field':'NOM','type':'ilike' },'dnu':{'field':'NDO','type':'startby' },'hcl':{'field':'HCL','type':'number' }}

    def search(self):
        self.make_special_conditions(request.args)
        self.cursor.execute("select top 100 NOM, NDO , HCL "
            "from CLIHCL "
            "where " + self.condition 
        )
        return self.cursor.fetchall()

    def browse(self,hcl):
        #super('pydtt_paciente', self).active_parameters={'dnu':{'field':'NDO','type':'string' },'hcl':{'field':'HCL','type':'number' }}
        #self.make_special_conditions(request.args)
        self.cursor.execute("select top 1 * "
            "from CLIHCL "
            "where HCL=%d" % (hcl) 
        )
        return self.cursor.fetchall()
    
    def browse_hc(self,hcl):
        #super('pydtt_paciente', self).active_parameters={'dnu':{'field':'NDO','type':'string' },'hcl':{'field':'HCL','type':'number' }}
        #self.make_special_conditions(request.args)
        result_set={}
        print ("select * "
            "from CLIHCL "
            "where HCL=%s" % (hcl) 
        )
        self.cursor.execute("select * "
            "from CLIHCL "
            "where HCL=%s" % (hcl) 
        )
        result_set['paciente']=self.cursor.fetchone()
        result_set['atenciones']=[]

        self.cursor.execute("select  * "
            "from CLIPAC pac "
            "where HCL=%s" %(hcl) 
        )

        for row in self.cursor.fetchall():
            item=row
            self.cursor.execute("select  tipo.DES ,  ope.NOM as operador , ev.FEC , ev.ORD,preg.LEY_1, "
                        "CASE  WHEN RSP_NUM  IS NULL THEN  TXT_LIB ELSE rsp.DES END  as respuesta "
                        "from CNSRSP  ev "
                        "join CNSANA  tipo on (ev.ANA=tipo.ANA) "
                        "join CNSPRG preg on (ev.PRG=preg.PRG) "
                        "left join CNSRPO rsp on (ev.PRG=rsp.PRG and ev.RSP_NUM=rsp.RSP) "
                        "join SYSOPE ope on (ev.OPE=ope.OPE) "
                        "where ev.PAC=%d" % (row['PAC']))
            item['preguntas']=self.cursor.fetchall()
            result_set['atenciones'].append(item)
        return result_set


class pydtt_crud(pyddt):

    def query(self):
        query = str(request.form['q'])
        self.cursor.execute(query)
        result_set= self.cursor.fetchall()
        return result_set
'''select  tipo.DES , preg.LEY_1 ,ev.*
 from CNSRSP  ev 
join CNSANA  tipo on (ev.ANA=tipo.ANA)
join    CNSPRG preg on (ev.PRG=preg.PRG)
 where ev.FEC > '2015-5-11' and OPE=443'''
