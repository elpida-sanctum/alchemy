import requests
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import config
import re
from collections import defaultdict
from netaddr import IPAddress, IPNetwork


appweb = Flask(__name__)
appweb.config.from_object('config')
dbase = SQLAlchemy(appweb)


class radreply(dbase.Model):
    id = dbase.Column(dbase.Integer, primary_key=True)
    username = dbase.Column(dbase.String(100))
    attribute = dbase.Column(dbase.String(100))
    op = dbase.Column(dbase.String(100))
    value = dbase.Column(dbase.String(100))


def dbase_add_apn(apn, ip, route):
    print(apn, ip, route)
    uname = apn + "/" + ip
    check = radreply.query.filter_by(username = uname, value = route).first()
    print(check)
    query = radreply(username=uname, attribute="Framed-Route",
                     op="+=", value=route)
    if check is None:
        dbase.session.add(query)
        dbase.session.commit()
        return True
    else:
        return False


def dbase_del_apn(id):
    radreply.query.filter_by(id = id).delete()
    dbase.session.commit()
    check = radreply.query.filter_by(id = id).first()
    if check is None:
        return True
    else:
        return False


@appweb.route('/')
def index():
    reps = radreply.query.all()
    return render_template("index.html", table=reps)


@appweb.route('/add')
def add():
    return render_template("add.html")


@appweb.route('/api/add_table', methods=['GET', 'POST'])
def add_table():
    if request.method == "POST":
        req = request.get_json()
        print("REQ=", req)
        resp_json = {}
        for line in req.values():
            print("line=", line)
            for id, val in enumerate(line):
                print(id, val)
                apn = val[0]
                ip = val[1]
                route = val[2]
                print("apn=",apn,"ip=",ip,"route=",route)
                res = dbase_add_apn(apn, ip, route)
                if res:
                    resp_json[id] = True
                elif not res:
                    resp_json[id] = False
        print(resp_json)
        return resp_json


@appweb.route('/api/validate', methods=['GET', 'POST'])
def validate():
    resp = {}
    apn_reg = re.compile(r"[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)")
    ip_reg = re.compile(r"\b(?:(?:2(?:[0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9])\.){3}(?:(?:2([0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9]))\b")
    route_reg = re.compile(r"\b(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))\b")
    regex_dict = {
        'apn': apn_reg,
        'ip': ip_reg,
        'route': route_reg,
    }
    if request.method == 'POST':
        req = request.get_json()
        print(req['apn'], req['ip'], req['route'])
        fields = ['apn', 'ip', 'route']
        for field in fields:
            valid = bool(re.fullmatch(regex_dict[field], req[field]))
            r = {
                "valid": valid,
                "value": req[field],
            }
            print(r)
            resp[field] = r
        print(resp)
        return resp


@appweb.route('/api/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        req = request.get_json()
        print(req)
        resp = dbase_del_apn(req['id'])
        print(resp)
        return {'deleted': resp}


@appweb.route('/api/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        req = request.files.get('file')
        fdata = req.stream.read().decode('utf-8')
        #print(fdata)
        flines = fdata.splitlines()
        result = {}
        for c, string in enumerate(flines):
            #print(string)
            cc = str(c)
            try:
                apn, ip, route = string.split()
            except ValueError:
                continue
            #print("apn: ", apn, "ip: ", ip, "route: ", route)
            dict = { 'apn': apn, 'ip': ip, 'route': route }
            res = requests.post('http://127.0.0.1:5000/api/validate', json=dict)
            resj = res.json()
            #print('response:', resj)
            d = {}
            for i in ['apn', 'ip', 'route']:
                if resj[i]['valid']:
                    d[i] = resj[i]['value']
            if len(d) == 3:
                result[cc] = d
        #print(result)
        return result


if __name__ == '__main__':
    appweb.run()
