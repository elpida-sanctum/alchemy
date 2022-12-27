import requests
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import config
import re
from collections import defaultdict
from netaddr import IPAddress, IPNetwork
import json 


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
    check = radreply.query.filter_by(username=uname, value=route).first()
    print(check)
    query = radreply(username=uname, attribute="Framed-Route",
                     op="+=", value=route)
    if check is None:
        dbase.session.add(query)
        dbase.session.commit()
        return True
    else:
        return False


def dbase_add_msisdn(msisdn, ip, type):
    print(msisdn, ip, type)
    if type == "IP Address":
        flag = True
    elif type == "Route":
        flag = False
    else:
        return False

    if flag:
        check = radreply.query.filter_by(
            username=msisdn, attribute="Framed-IP-Address").first()
        print(check)
        query = radreply(username=msisdn, attribute="Framed-IP-Address",
                         op=":=", value=ip)
    else:
        check = radreply.query.filter_by(
            username=msisdn, attribute="Framed-Route").first()
        print(check)
        query = radreply(username=msisdn, attribute="Framed-Route",
                         op="+=", value=ip)
    if check is None:
        dbase.session.add(query)
        dbase.session.commit()
        return True
    else:
        return False


def dbase_del(id):
    radreply.query.filter_by(id=id).delete()
    dbase.session.commit()
    check = radreply.query.filter_by(id=id).first()
    if check is None:
        return True
    else:
        return False


@appweb.route('/')
def index():
    reps = radreply.query.all()
    return render_template("index.html", table=reps)


@appweb.route('/add_apn')
def add_apn():
    return render_template("apn.html")


@appweb.route('/add_msisdn')
def add_msisdn():
    return render_template("msisdn.html")


@appweb.route('/api/add_apn', methods=['GET', 'POST'])
def send_apn_to_db():
    if request.method == "POST":
        req = request.get_json()
        resp_json = {}
        print(type(req), ": request: ", req)
        for num, line in enumerate(req['dataT']):
            print(type(line), ": line: ", line)
            #for val in line:
            apn = line['apn']
            ip = line['ip']
            route = line['route']
            res = dbase_add_apn(apn, ip, route)
            if res:
                resp_json[num] = True
            elif not res:
                resp_json[num] = False
        print("response: ", resp_json)
        return resp_json


@appweb.route('/api/add_apn_tab', methods=['GET', 'POST'])
def send_apn_to_db_tab():
    if request.method == "POST":
        req = request.get_json()
        resp_json = {}
        for id, val in req:
            apn = val[0]
            ip = val[1]
            route = val[2]
            res = dbase_add_apn(apn, ip, route)
            if res:
                resp_json[id] = True
            elif not res:
                resp_json[id] = False
        print(resp_json)
        return resp_json


@appweb.route('/api/add_msisdn', methods=['GET', 'POST'])
def send_msisdn_to_db():
    if request.method == "POST":
        req = request.get_json()
        print(req)
        resp_json = {}
        for line in req.values():
            for id, val in enumerate(line):
                msisdn = val[0]
                ipr = val[1]
                type = val[2]
                res = dbase_add_msisdn(msisdn, ipr, type)
                if res:
                    resp_json[id] = True
                elif not res:
                    resp_json[id] = False
        print(resp_json)
        return resp_json


@appweb.route('/api/validate', methods=['GET', 'POST'])
def validate():
    resp = {}
    msisdn_reg = re.compile(r"79[0-9]{9}")
    apn_reg = re.compile(
        r"[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)")
    ip_reg = re.compile(
        r"\b(?:(?:2(?:[0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9])\.){3}(?:(?:2([0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9]))\b")
    route_reg = re.compile(
        r"\b(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))\b")
    regex_dict = {
        'msisdn': msisdn_reg,
        'apn': apn_reg,
        'ip': ip_reg,
        'route': route_reg,
    }
    if request.method == 'POST':
        req = request.get_json()
        print(req)
        fields = ['msisdn', 'apn', 'ip', 'route']
        for field in fields:
            try:
                valid = bool(re.fullmatch(regex_dict[field], req[field]))
                r = {
                    "valid": valid,
                    "value": req[field],
                }
                print(r)
                resp[field] = r
            except KeyError:
                continue
        print(resp)
        return resp


@appweb.route('/api/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        req = request.get_json()
        print(req)
        resp = dbase_del(req['id'])
        print(resp)
        return {'deleted': resp}


@appweb.route('/api/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        #type = request.get('type')
        # print(type)
        req = request.files.get('file')
        fdata = req.stream.read().decode('utf-8')
        # print(fdata)
        flines = fdata.splitlines()
        result = {}
        for c, string in enumerate(flines):
            # print(string)
            cc = str(c)
            try:
                apn, ip, route = string.split()
            except ValueError:
                continue
            #print("apn: ", apn, "ip: ", ip, "route: ", route)
            dict = {'apn': apn, 'ip': ip, 'route': route}
            res = requests.post(
                'http://127.0.0.1:5000/api/validate', json=dict)
            resj = res.json()
            #print('response:', resj)
            d = {}
            for i in ['apn', 'ip', 'route']:
                if resj[i]['valid']:
                    d[i] = resj[i]['value']
            if len(d) == 3:
                result[cc] = d
        # print(result)
        return result


if __name__ == '__main__':
    appweb.run()
