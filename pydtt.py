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
            "( (convert (INT, pac.INS) > 4300 and convert (INT, pac.INS) < 4999) "
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
    active_parameters={'nombre':'pac.NOM','HCL':'hcl.HCL'}

    def get_from_time(self,start_time):
        self.cursor.execute("select  ORI, PAC , pac.NOM , pac.DIR , pac.LOC, pac.CPO, pac.TEL, pac.FNA, pac.SEX,  pac.NDO, "
            "pac.INS, pac.HCL , FIN "
            "from CLIPAC pac "
            "left join CLIHCL hcl on (pac.HCL = hcl.HCL ) "
            "where ORI='A' "
            "and FIN>= '%s' and ISNUMERIC(pac.INS)=1 and "
            "( (convert (INT, pac.INS) > 4300 and convert (INT, pac.INS) < 4999) ) " % (start_time)
        )

        return self.cursor.fetchall()

    def search(self):

        self.cursor.execute("select INS, DES,DIR,LOC,CPO,CUI,NGA "
            "from dbo.CLINST "
            "where INS not like 'm%' and ISNUMERIC(INS)=1 and "
            "( (convert (INT, pac.INS) > 4300 and convert (INT, pac.INS) < 4999) "
            "and DES like '%(cond)s'"  % filters
        )
        return self.cursor.fetchall()



class pydtt_paciente(pyddt):
    active_parameters={'nombre':'pac.NOM','HCL':'hcl.HCL'}

    def get_from_time(self,start_time):
        self.cursor.execute("select  ORI, PAC , pac.NOM , pac.DIR , pac.LOC, pac.CPO, pac.TEL, pac.FNA, pac.SEX,  pac.NDO, "
            "pac.INS, pac.HCL , FIN "
            "from CLIPAC pac "
            "left join CLIHCL hcl on (pac.HCL = hcl.HCL ) "
            "where ORI='A' "
            "and FIN>= '%s' and ISNUMERIC(pac.INS)=1 and "
            "( (convert (INT, pac.INS) > 4300 and convert (INT, pac.INS) < 4999) ) " % (start_time)
        )

        return self.cursor.fetchall()

    def search(self):

        self.cursor.execute("select INS, DES,DIR,LOC,CPO,CUI,NGA "
            "from dbo.CLINST "
            "where INS not like 'm%' and ISNUMERIC(INS)=1 and "
            "( (convert (INT, pac.INS) > 4300 and convert (INT, pac.INS) < 4999) "
            "and DES like '%(cond)s'"  % filters
        )
        return self.cursor.fetchall()



