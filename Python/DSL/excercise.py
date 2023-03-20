import json
import socket
import threading
import time
import pymysql
from flask import Flask, request, jsonify
from flask_cors import CORS
from select import select
import socket

socket.setdefaulttimeout(500)

# 打开数据库连接                127.0.0.1
Tang = pymysql.connect(host="localhost", port=3306, user="root", password="dsl123", database="excercise",
                       charset="utf8")
xiao = Tang.cursor()

def reconnect():
    # TODO: add auto reconnect
    try:
        db = pymysql.connect(host="localhost", port=3306, user="root", password="dsl123", database="excercise",
                             charset="utf8")
        return db
    except pymysql.Error as e:
        print("Mysql Error: %s" % (e,))
        return False


app = Flask(__name__)
CORS(app, resource=r'/*')  # 解决跨域问题

isChange = False
LightChange = False
FanChange = False
TwofanChange = False
ElceChange = False
revChange = False
trevChange = False
# ——————————————————————下发指令符——————————————--————

event = threading.Event


def hhhh():
    # 1.创建套接字 socket
    global isChange, LightChange, ElceChange, FanChange, TwofanChange, revChange,  trevChange
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 设置为非阻塞模式
    server.setblocking(0)

    # 端口复用
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # server.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 60*1000, 30*1000))

    # 2.绑定 bind
    server.bind(('192.168.100.174', 9040))
    # server.bind(('192.168.0.197', 9040))
    # server.bind(('192.168.31.247', 9040))
    # server.bind(('192.168.43.60', 9040))
    # ——————————————————————IP地址需要改——————————————--————

    # 3.监听 listen
    server.listen(5)

    print('starting...')

    # 设置关注列表
    # 初始化读取数据监听列表，最开始时希望从server这个套接字上读取数据。监听套接字:server 只有读操作，等待客户端连接
    rlist = [server]
    # 初始化写入数据的监听列表，最开始并没有客户端连接进来，所以列表为空
    wlist = []
    xlist = []

    while True:
        # 监控IO发生
        # select函数语法: rs,ws,xs=select(rlist, wlist, xlist[, timeout])
        # 提交监测我们关注的IO，阻塞等待IO发生
        rs, ws, xs = select(rlist, wlist, xlist)
        for r in rs:  # 遍历读列表(收到客户端请求的对象)
            if r is server:  # 分情况讨论，如果是监听套接字，说明由客户端连接服务端，做以下事情(只能读)
                #
                c, client_addr = r.accept()   # 如果是server套接字对象接收到请求，则说明是新的用户连接
                print(client_addr)
                c.setblocking(0)
                rlist.append(c)  # 将新生成的套接字添加到读监听列表list中，让操作系统去监控
                wlist.append(c)
                xlist.append(c)
                time.sleep(3)
            else:  # 如果不是server套接字对象接收的请求，则说明是已有的现成连接，以便保持持续的连接
                cmd = r.recv(1024).decode('utf-8')  # 接收客户端传过来的数据,数据是不是uft-8类型的，大小最多1024个字节
                if not cmd:  # 如果没有发送过来任何数据
                    rlist.remove(r)  # 将当前套接字移除出rlist列表，使select不再监管此对象
                    r.close()  # 将当前套接字关闭
                else:
                    data_res = cmd
                    print(data_res)
                    # print(str(data_res))
                    # result = json.loads(data_res)
                    result = json.loads(data_res, strict=False)
                    print(result)
                    print(type(result))
                    # ——————————————————————服务器与数据库，一一对应——————————————--————
                    logo = result.get('ID1')
                    logo2 = result.get('ID2')
                    temp = result.get('wendu')
                    temp2 = result.get('wendu2')
                    volt = result.get('dianya')
                    volt2 = result.get('dianya2')
                    cur = result.get('dianliu')
                    cur2 = result.get('dianliu2')
                    rev = result.get('zhuansu')
                    rev2 = result.get('zhuansu2')
                    lux = result.get('guangzhao')
                    lux2 = result.get('guangzhao2')
                    lon = result.get('jingdu')
                    lon2 = result.get('jingdu2')
                    lat = result.get('weidu')
                    lat2 = result.get('weidu2')
                    alt = result.get('haiba')
                    alt2 = result.get('haiba2')
                    print(logo, logo2, temp, temp2, volt, volt2,  cur, cur2, rev, rev2, lux, lux2, lon, lon2,
                          lat, lat2, alt, alt2)
                    xiao.execute("insert into data(ID1,ID2,wendu,wendu2,dianya,dianya2,dianliu,dianliu2,zhuansu,zhuansu2,"
                                 "guangzhao,guangzhao2,jingdu,jingdu2,weidu,weidu2,haiba,haiba2) values (\"" + str(logo) +
                                 "\",\"" + str(logo2) + "\",\"" + str(temp) + "\",\"" + str(temp2) +
                                 "\",\"" + str(volt) + "\",\"" + str(volt2) + "\",\"" + str(cur) +
                                 "\",\"" + str(cur2) + "\",\"" + str(rev) + "\",\"" + str(rev2) +
                                 "\",\"" + str(lux) + "\",\"" + str(lux2) + "\",\"" + str(lon) +
                                 "\",\"" + str(lon2) + "\",\"" + str(lat) + "\",\"" + str(lat2) +
                                 "\",\"" + str(alt) + "\",\"" + str(alt2) + "\")")
                    # ——————————————————————服务器与数据库，一一对应——————————————--————
                    Tang.commit()  # 提交，使操作生效
                    print("add  successfully!")
                    print("接收到数据")
                    datacmd_dic = {'status': 'ok'}
                    datacmd_json = json.dumps(datacmd_dic)  # json格式的字符串
                    datacmd_bytes = datacmd_json.encode('utf-8')  # 将报头格式转换为bytes
                    r.send(datacmd_bytes)
                    print(datacmd_bytes)
                    print("响应已经全部发送")

            for i in range(1):
                for w in ws:
                    if isChange:
                        print(isChange)
                        xiao.execute("select wfazhigao,wfazhidi,dfazhigao,dfazhidi,zfazhigao,zfazhidi,gfazhigao,gfazhidi,"
                                     "wfazhigao2,wfazhidi2,dfazhigao2,dfazhidi2,zfazhigao2,zfazhidi2,gfazhigao2,gfazhidi2 from threshold")
                        data = xiao.fetchone()
                        print("oh~")
                        if (data != None):
                            print("result:", data)
                            jsondata = {"wfazhigao": str(data[0]), "wfazhidi": str(data[1]),
                                        "dfazhigao": str(data[2]), "dfazhidi": str(data[3]),
                                        "zfazhigao": str(data[4]), "zfazhidi": str(data[5]),
                                        "gfazhigao": str(data[6]), "gfazhidi": str(data[7]),
                                        "wfazhigao2": str(data[8]), "wfazhidi2": str(data[9]),
                                        "dfazhigao2": str(data[10]), "dfazhidi2": str(data[11]),
                                        "zfazhigao2": str(data[12]), "zfazhidi2": str(data[13]),
                                        "gfazhigao2": str(data[14]), "gfazhidi2": str(data[15])
                                        }

                        postcmd_dic = {
                            'data': {"wfazhigao": str(data[0]), "wfazhidi": str(data[1]),
                                     "dfazhigao": str(data[2]), "dfazhidi": str(data[3]),
                                     "zfazhigao": str(data[4]), "zfazhidi": str(data[5]),
                                     "gfazhigao": str(data[6]), "gfazhidi": str(data[7]),
                                     "wfazhigao2": str(data[8]), "wfazhidi2": str(data[9]),
                                     "dfazhigao2": str(data[10]), "dfazhidi2": str(data[11]),
                                     "zfazhigao2": str(data[12]), "zfazhidi2": str(data[13]),
                                     "gfazhigao2": str(data[14]), "gfazhidi2": str(data[15])
                                     }}
                        postcmd_json = json.dumps(postcmd_dic)  # json格式的字符串
                        postcmd_str = postcmd_json.replace(" ", "")
                        postcmd_bytes = postcmd_str.encode('utf-8')  # 将报头格式转换为bytes
                        r.send(postcmd_bytes)
                        print(postcmd_bytes)
                        print("命令下发成功")
                        precmd_dic = {'status': 'finish'}
                        precmd_json = json.dumps(precmd_dic)  # json格式的字符串
                        precmd_bytes = precmd_json.encode('utf-8')  # 将报头格式转换为bytes
                        r.send(precmd_bytes)
                        print(precmd_bytes)
                        print("命令已经全部发送")
                        isChange = False

                    elif revChange:
                        print(revChange)
                        xiao.execute("select speed from state")
                        data = xiao.fetchone()
                        print("oh~")
                        if (data != None):
                            print("result:", data)
                            jsondata = {"speed": str(data[0])}

                        speedcmd_dic = {
                            'data': {"speed": str(data[0])}}
                        speedcmd_json = json.dumps(speedcmd_dic)  # json格式的字符串
                        speedcmd_str = speedcmd_json.replace(" ", "")
                        speedcmd_bytes = speedcmd_str.encode('utf-8')  # 将报头格式转换为bytes
                        r.send(speedcmd_bytes)
                        print(speedcmd_bytes)
                        print("命令下发成功")
                        spdcmd_dic = {'status': 'finish'}
                        spdcmd_json = json.dumps(spdcmd_dic)  # json格式的字符串
                        spdcmd_bytes = spdcmd_json.encode('utf-8')  # 将报头格式转换为bytes
                        r.send(spdcmd_bytes)
                        print(spdcmd_bytes)
                        print("命令已经全部发送")
                        revChange = False

                    elif trevChange:
                        print(trevChange)
                        xiao.execute("select speed2 from state")
                        data = xiao.fetchone()
                        print("oh~")
                        if (data != None):
                            print("result:", data)
                            jsondata = {"speed2": str(data[0])}

                        tspeedcmd_dic = {
                            'data': {"speed2": str(data[0])}}
                        tspeedcmd_json = json.dumps(tspeedcmd_dic)  # json格式的字符串
                        tspeedcmd_str = tspeedcmd_json.replace(" ", "")
                        tspeedcmd_bytes = tspeedcmd_str.encode('utf-8')  # 将报头格式转换为bytes
                        r.send(tspeedcmd_bytes)
                        print(tspeedcmd_bytes)
                        print("命令下发成功")
                        tspdcmd_dic = {'status': 'finish'}
                        tspdcmd_json = json.dumps(tspdcmd_dic)  # json格式的字符串
                        tspdcmd_bytes = tspdcmd_json.encode('utf-8')  # 将报头格式转换为bytes
                        r.send(tspdcmd_bytes)
                        print(tspdcmd_bytes)
                        print("命令已经全部发送")
                        trevChange = False

                    elif LightChange:
                        xiao.execute("select light from state")
                        data = xiao.fetchone()
                        if (data != None):
                            print("result:", data)
                            jsondata = {"light": str(data[0])}
                        Lightcmd_dic = {'switch': {'light': str(data[0])}, 'status': 'finish'}
                        Lightcmd_json = json.dumps(Lightcmd_dic)  # json格式的字符串
                        Lightcmd_str = Lightcmd_json.replace(" ", "")
                        Lightcmd_bytes = Lightcmd_str.encode('utf-8')  # 将报头格式转换为bytes
                        r.send(Lightcmd_bytes)
                        print(Lightcmd_bytes)
                        print("灯光命令下发成功")
                        LightChange = False

                    elif ElceChange:
                        xiao.execute("select elce from state")
                        data = xiao.fetchone()
                        print("oh~")
                        if (data != None):
                            print("result:", data)
                            jsondata = {"elce": str(data[0])}
                        Elcecmd_dic = {'switch': {'elce': str(data[0])}, 'status': 'finish'}
                        Elcecmd_json = json.dumps(Elcecmd_dic)  # json格式的字符串
                        Elcecmd_str = Elcecmd_json.replace(" ", "")
                        Elcecmd_bytes = Elcecmd_str.encode('utf-8')  # 将报头格式转换为bytes
                        r.send(Elcecmd_bytes)
                        print(Elcecmd_bytes)
                        print("电机命令下发成功")
                        ElceChange = False

                    elif FanChange:
                        xiao.execute("select fan from state")
                        data = xiao.fetchone()
                        print("oh~")
                        if (data != None):
                            print("result:", data)
                            jsondata = {"fan": str(data[0])}
                        Fancmd_dic = {'switch': {'fan': str(data[0])}, 'status': 'finish'}
                        Fancmd_json = json.dumps(Fancmd_dic)  # json格式的字符串
                        Fancmd_str = Fancmd_json.replace(" ", "")
                        Fancmd_bytes = Fancmd_str.encode('utf-8')  # 将报头格式转换为bytes
                        r.send(Fancmd_bytes)
                        print(Fancmd_bytes)
                        print("风扇1命令下发成功")
                        FanChange = False

                    elif TwofanChange:
                        xiao.execute("select twofan from state")
                        data = xiao.fetchone()
                        print("oh~")
                        if (data != None):
                            print("result:", data)
                            jsondata = {"twofan": str(data[0])}
                        Twofancmd_dic = {'switch': {'twofan': str(data[0])}, 'status': 'finish'}
                        Twofancmd_json = json.dumps(Twofancmd_dic)  # json格式的字符串
                        Twofancmd_str = Twofancmd_json.replace(" ", "")
                        Twofancmd_bytes = Twofancmd_str.encode('utf-8')  # 将报头格式转换为bytes
                        r.send(Twofancmd_bytes)
                        print(Twofancmd_bytes)
                        print("风扇2命令下发成功")
                        TwofanChange = False
                    else:
                        print("failed")

# {"ID1":"SN666","ID2":"JJ555","wendu":15,"wendu2":21,"dianya":3.3,"dianya2":5.1,"dianliu":0.11,"dianliu2":0.12,"zhuansu":300,"zhuansu2":500,"guangzhao":50,"guangzhao2":80,"jingdu":"111.39E","jingdu2":"111.39E","weidu":"29.3N","weidu2":"29.3N","haiba":42.1,"haiba2":41.3}
# {"status": "finish"}
# {"switch": {"elce": "on"}, "status": "finish"}

# 后端接口的入口  参数1：后端接口的路径  参数2：方法
# 获取所有用户信息
@app.route('/login/list', methods=['POST'])
def login_list():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select id,username from login")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["id"] = i[0]
                temp["username"] = i[1]
                result.append(temp.copy())  # 特别注意要用copy，否则只是内存的引用
            print("result:", len(data))
            return jsonify(result)
        else:
            print("result: NULL")
            return jsonify([])

# 用户登录验证
@app.route('/login', methods=['POST'])
def login_check():
    db = reconnect()
    cursor = db.cursor()
    if request.method == 'POST':
        username = request.values.get("username")
        password = request.values.get("password")
        print(username)
        print(password)
        # db.ping(reconnect=True)
        cursor.execute("select id,username,password from login where username=\""
                       + str(username) + "\" and password=\"" + str(password) + "\"")
        data = cursor.fetchone()
        if (data!=None):
            print("result:", data)
            jsondata = {"id": str(data[0]), "username": str(data[1]), "password": str(data[2])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            # jsondata = {}
            return "-1"   # jsonify(jsondata)

# 添加新用户
@app.route('/login/add', methods=['POST'])
def login_add():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        username = request.values.get("username")
        password = request.values.get("password")
        try:
            cursor.execute("insert into login(username,password) values (\""
                           + str(username) + "\",\"" + str(password) + "\")")
            db.commit()  # 提交，使操作生效，数据库才会增加
            print("add a new user successfully!")
            return "1"
        except Exception as e:
            print("add a new user failed:", e)
            db.rollback()  # 发生错误就回滚，将错误操作撤回
            return "-1"

# 修改密码
@app.route('/login/update', methods=['POST'])
def login_update():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        username = request.values.get("username")
        password = request.values.get("password")
        try:
            cursor.execute("update login set password=\"" + str(password) + "\" where username=\"" + str(username) + "\" ")
            db.commit()
            print("update password successfully!")
            return "1"
        except Exception as e:
            print("update password failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 上传某一数据
# 上传温度的数据，其余默认为null.
@app.route('/data/addwendu', methods=['POST'])
def data_addwendu():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        wendu = request.values.get("wendu")
        wendu2 = request.values.get("wendu2")
        try:
            cursor.execute("insert into data(wendu,wendu2) values(\"" + str(wendu) + "\",\"" + str(wendu2) + "\")")
            db.commit()  # 提交，使操作生效
            print("add successfully!")
            return "1"
        except Exception as e:
            print("add failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 上传电压数据
@app.route('/data/adddianya', methods=['POST'])
def data_adddianya():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        dianya = request.values.get("dianya")
        dianya2 = request.values.get("dianya2")
        try:
            cursor.execute("insert into data(dianya,dianya2) values (\"" + str(dianya) +
                           "\",\"" + str(dianya2) + "\")")
            db.commit()  # 提交，使操作生效
            print("add  successfully!")
            return "1"
        except Exception as e:
            print("add failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 上传电流数据
@app.route('/data/adddianliu', methods=['POST'])
def data_adddianliu():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        dianliu = request.values.get("dianliu")
        dianliu2 = request.values.get("dianliu2")
        try:
            cursor.execute("insert into data(dianliu,dianliu2) values (\"" + str(dianliu) +
                           "\",\"" + str(dianliu2) + "\")")
            db.commit()  # 提交，使操作生效
            print("add  successfully!")
            return "1"
        except Exception as e:
            print("add failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 上传转速数据
@app.route('/data/addzhuansu', methods=['POST'])
def data_addzhuansu():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        zhuansu = request.values.get("zhuansu")
        zhuansu2 = request.values.get("zhuansu2")
        try:
            cursor.execute("insert into data(zhuansu,zhuansu2) values (\"" + str(zhuansu) +
                           "\",\"" + str(zhuansu2) + "\")")
            db.commit()  # 提交，使操作生效
            print("add  successfully!")
            return "1"
        except Exception as e:
            print("add failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 上传光照数据
@app.route('/data/addguangzhao', methods=['POST'])
def data_addguangzhao():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        guangzhao = request.values.get("guangzhao")
        guangzhao2 = request.values.get("guangzhao2")
        try:
            cursor.execute("insert into data(guangzhao,guangzhao2) values (\""
                           + str(guangzhao) + "\",\"" + str(guangzhao2) + "\")")
            db.commit()  # 提交，使操作生效
            print("add  successfully!")
            return "1"
        except Exception as e:
            print("add failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 上传ID号
@app.route('/data/addID', methods=['POST'])
def data_addID():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        ID1 = request.values.get("ID1")
        ID2 = request.values.get("ID2")
        try:
            cursor.execute("insert into data(ID1,ID2) values (\""
                           + str(ID1) + "\",\"" + str(ID2) + "\")")
            db.commit()  # 提交，使操作生效
            print("add  successfully!")
            return "1"
        except Exception as e:
            print("add failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 上传经度
@app.route('/data/addjingdu', methods=['POST'])
def data_addjingdu():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        jingdu = request.values.get("jingdu")
        jingdu2 = request.values.get("jingdu2")
        try:
            cursor.execute("insert into data(jingdu,jingdu2) values (\""
                           + str(jingdu) + "\",\"" + str(jingdu2) + "\")")
            db.commit()  # 提交，使操作生效
            print("add successfully!")
            return "1"
        except Exception as e:
            print("add failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 上传纬度
@app.route('/data/addweidu', methods=['POST'])
def data_addweidu():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        weidu = request.values.get("weidu")
        weidu2 = request.values.get("weidu2")
        try:
            cursor.execute("insert into data(weidu,weidu2) values (\"" + str(weidu) + "\",\"" + str(weidu2) + "\")")
            db.commit()  # 提交，使操作生效
            print("add  successfully!")
            return "1"
        except Exception as e:
            print("add failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 上传海拔
@app.route('/data/addhaiba', methods=['POST'])
def data_addhaiba():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        haiba = request.values.get("haiba")
        haiba2 = request.values.get("haiba2")
        try:
            cursor.execute("insert into data(haiba,haiba2) values (\""
                           + str(haiba) + "\",\"" + str(haiba2) + "\")")
            db.commit()  # 提交，使操作生效
            print("add  successfully!")
            return "1"
        except Exception as e:
            print("add failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 查询所有的数据
@app.route('/data/check_all', methods=['POST'])
def data_check_all():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        print(request)
        cursor.execute("select ID1 from data ")
        dataID1 = cursor.fetchall()

        cursor.execute("select ID2 from data ")
        dataID2 = cursor.fetchall()

        cursor.execute("select wendu from data ")
        datawendu = cursor.fetchall()

        cursor.execute("select wendu2 from data ")
        datawendu2 = cursor.fetchall()

        cursor.execute("select dianya from data ")
        datadianya = cursor.fetchall()

        cursor.execute("select dianya2 from data ")
        datadianya2 = cursor.fetchall()

        cursor.execute("select dianliu from data ")
        datadianliu = cursor.fetchall()

        cursor.execute("select dianliu2 from data ")
        datadianliu2 = cursor.fetchall()

        cursor.execute("select zhuansu from data ")
        datazhuansu = cursor.fetchall()

        cursor.execute("select zhuansu2 from data ")
        datazhuansu2 = cursor.fetchall()

        cursor.execute("select guangzhao from data ")
        dataguangzhao = cursor.fetchall()

        cursor.execute("select guangzhao2 from data ")
        dataguangzhao2 = cursor.fetchall()

        cursor.execute("select jingdu from data ")
        datajingdu = cursor.fetchall()

        cursor.execute("select jingdu2 from data ")
        datajingdu2 = cursor.fetchall()

        cursor.execute("select weidu from data ")
        dataweidu = cursor.fetchall()

        cursor.execute("select weidu2 from data ")
        dataweidu2 = cursor.fetchall()

        cursor.execute("select haiba from data ")
        datahaiba = cursor.fetchall()

        cursor.execute("select haiba2 from data ")
        datahaiba2 = cursor.fetchall()

        cursor.execute("select creat_time from data ")
        dataTime = cursor.fetchall()
        # print(dataTime)
        tempTime = []
        for i in dataTime:
            if (i[0] != None):
                tempTime.append(i[0].timestamp())
            else:
                tempTime.append("0")
        result = {
            "ID1": dataID1,
            "ID2": dataID2,
            "wendu": datawendu,
            "wendu2": datawendu2,
            "dianya": datadianya,
            "dianya2": datadianya2,
            "dianliu": datadianliu,
            "dianliu2": datadianliu2,
            "zhuansu": datazhuansu,
            "zhuansu2": datazhuansu2,
            "guangzhao": dataguangzhao,
            "guangzhao2": dataguangzhao2,
            "jingdu": datajingdu,
            "jingdu2": datajingdu2,
            "weidu": dataweidu,
            "weidu2": dataweidu2,
            "haiba": datahaiba,
            "haiba2": datahaiba2,
            "creat_time": dataTime,
        }
        return jsonify(result)


# 查询最新上传的所有数据
@app.route('/data/allNews', methods=['POST'])
def data_checknewAll():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        cursor.execute("select ID1 from data order by id desc limit 1")
        newID1 = cursor.fetchone()

        cursor.execute("select ID2 from data order by id desc limit 1")
        newID2 = cursor.fetchone()

        cursor.execute("select wendu from data order by id desc limit 1")
        newwendu = cursor.fetchone()

        cursor.execute("select wendu2 from data order by id desc limit 1")
        newwendu2 = cursor.fetchone()

        cursor.execute("select dianya from data order by id desc limit 1")
        newdianya = cursor.fetchone()

        cursor.execute("select dianya2 from data order by id desc limit 1")
        newdianya2 = cursor.fetchone()

        cursor.execute("select dianliu from data order by id desc limit 1")
        newdianliu = cursor.fetchone()

        cursor.execute("select dianliu2 from data order by id desc limit 1")
        newdianliu2 = cursor.fetchone()

        cursor.execute("select zhuansu from data order by id desc limit 1")
        newzhuansu = cursor.fetchone()

        cursor.execute("select zhuansu2 from data order by id desc limit 1")
        newzhuansu2 = cursor.fetchone()

        cursor.execute("select guangzhao from data order by id desc limit 1")
        newguangzhao = cursor.fetchone()

        cursor.execute("select guangzhao2 from data order by id desc limit 1")
        newguangzhao2 = cursor.fetchone()

        cursor.execute("select jingdu from data order by id desc limit 1")
        newjingdu = cursor.fetchone()

        cursor.execute("select jingdu2 from data order by id desc limit 1")
        newjingdu2 = cursor.fetchone()

        cursor.execute("select weidu from data order by id desc limit 1")
        newweidu = cursor.fetchone()

        cursor.execute("select weidu2 from data order by id desc limit 1")
        newweidu2 = cursor.fetchone()

        cursor.execute("select haiba from data order by id desc limit 1")
        newhaiba = cursor.fetchone()

        cursor.execute("select haiba2 from data order by id desc limit 1")
        newhaiba2 = cursor.fetchone()

        cursor.execute("select creat_time from data order by id desc limit 1")
        newCreat_time = cursor.fetchone()

        jsondata = {
            "ID1": str(newID1[0]),
            "ID2": str(newID2[0]),
            "wendu": str(newwendu[0]),
            "wendu2": str(newwendu2[0]),
            "dianya": str(newdianya[0]),
            "dianya2": str(newdianya2[0]),
            "dianliu": str(newdianliu[0]),
            "dianliu2": str(newdianliu2[0]),
            "zhuansu": str(newzhuansu[0]),
            "zhuansu2": str(newzhuansu2[0]),
            "guangzhao": str(newguangzhao[0]),
            "guangzhao2": str(newguangzhao2[0]),
            "jingdu": str(newjingdu[0]),
            "jingdu2": str(newjingdu2[0]),
            "weidu": str(newweidu[0]),
            "weidu2": str(newweidu2[0]),
            "haiba": str(newhaiba[0]),
            "haiba2": str(newhaiba2[0]),
            "creat_time": str(newCreat_time[0])
        }
        return jsonify(jsondata)


# 查询最新上传的某一数据
# 查询ID号
@app.route('/data/checkID', methods=['POST'])
def data_checkID():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select ID1,ID2,creat_time from data order by id desc limit 1")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"ID1": str(data[0]), "ID2": str(data[1]), "creat_time": str(data[2])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 查询最新温度数据
@app.route('/data/checkwendu', methods=['POST'])
def data_checkwendu():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select wendu,wendu2,creat_time from data order by id desc limit 1")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"wendu": str(data[0]), "wendu2": str(data[1]), "creat_time": str(data[2])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 查询最新电压数据
@app.route('/data/checkdianya', methods=['POST'])
def data_checkdianya():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select dianya,dianya2,creat_time from data order by id desc limit 1")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"dianya": str(data[0]), "dianya2": str(data[1]), "creat_time": str(data[2])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 查询最新电流数据
@app.route('/data/checkdianliu', methods=['POST'])
def data_checkdianliu():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select dianliu,dianliu2,creat_time from data order by id desc limit 1")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"dianliu": str(data[0]), "dianliu2": str(data[1]), "creat_time": str(data[2])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 查询最新转速数据
@app.route('/data/checkzhuansu', methods=['POST'])
def data_checkzhuansu():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select zhuansu,zhuansu2,creat_time from data order by id desc limit 1")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"zhuansu": str(data[0]), "zhuansu2": str(data[1]), "creat_time": str(data[2])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 查询最新光照数据
@app.route('/data/checkguangzhao', methods=['POST'])
def data_checkguangzhao():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select guangzhao,guangzhao2,creat_time from data order by id desc limit 1")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"guangzhao": str(data[0]), "guangzhao2": str(data[1]), "creat_time": str(data[2])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 查询最新经度数据
@app.route('/data/checkjingdu', methods=['POST'])
def data_checkjingdu():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select jingdu,jingdu2,creat_time from data order by id desc limit 1")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"jingdu": str(data[0]), "jingdu2": str(data[1]), "creat_time": str(data[2])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 查询最新纬度数据
@app.route('/data/checkweidu', methods=['POST'])
def data_checkweidu():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select weidu,weidu2,creat_time from data order by id desc limit 1")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"weidu": str(data[0]), "weidu2": str(data[1]), "creat_time": str(data[2])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 查询最新海拔数据
@app.route('/data/checkhaiba', methods=['POST'])
def data_checkhaiba():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select haiba,haiba2,creat_time from data order by id desc limit 1")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"hiaba": str(data[0]), "haiba2": str(data[1]), "creat_time": str(data[2])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)


# 以传感器类型为条件，查询历史数据
# 查询温度历史数据
@app.route('/data/wendu_checkall', methods=['POST'])
def data_wendu_checkall():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        if request.method == "POST":
            db.ping(reconnect=True)
            cursor.execute("select wendu,wendu2,creat_time from data")
            data = cursor.fetchall()
            temp = {}
            result = []
            if (data != None):
                for i in data:
                    temp["wendu"] = str(i[0])
                    temp["wendu2"] = str(i[1])
                    temp["creat_time"] = str(i[2])
                    result.append(temp.copy())
                print("result:", data)
                print("result_length:", len(data))
                return jsonify(result)
            else:
                print("result:NULL")
                jsondata = {}
                return jsonify([])

# 查询电压历史数据
@app.route('/data/dianya_checkall', methods=['POST'])
def data_dianya_checkall():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select dianya,dianya2,creat_time from data")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["dianya"] = str(i[0])
                temp["dianya2"] = str(i[1])
                temp["creat_time"] = str(i[2])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 查询电流历史数据
@app.route('/data/dianliu_checkall', methods=['POST'])
def data_dianliu_checkall():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select dianliu,dianliu2,creat_time from data")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["dianliu"] = str(i[0])
                temp["dianliu2"] = str(i[1])
                temp["creat_time"] = str(i[2])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 查询转速历史数据
@app.route('/data/zhuansu_checkall', methods=['POST'])
def data_zhuansu_checkall():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select zhuansu,zhuansu2,creat_time from data")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["zhuansu"] = str(i[0])
                temp["zhuansu2"] = str(i[1])
                temp["creat_time"] = str(i[2])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 查询光照历史数据
@app.route('/data/guangzhao_checkall', methods=['POST'])
def data_guangzhao_checkall():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select guangzhao,guangzhao2,creat_time from data")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["guangzhao"] = str(i[0])
                temp["guangzhao2"] = str(i[1])
                temp["creat_time"] = str(i[2])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 查询经度历史数据
@app.route('/data/jingdu_checkall', methods=['POST'])
def data_jingdu_checkall():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select jingdu,jingdu2,creat_time from data")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["jingdu"] = str(i[0])
                temp["jingdu2"] = str(i[1])
                temp["creat_time"] = str(i[2])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 查询纬度历史数据
@app.route('/data/weidu_checkall', methods=['POST'])
def data_weidu_checkall():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select weidu,weidu2,creat_time from data")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["weidu"] = str(i[0])
                temp["weidu2"] = str(i[1])
                temp["creat_time"] = str(i[2])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 查询海拔历史数据
@app.route('/data/haiba_checkall', methods=['POST'])
def data_haiba_checkall():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select haiba,haiba2,creat_time from data")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["haiba"] = str(i[0])
                temp["haiba2"] = str(i[1])
                temp["creat_time"] = str(i[2])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 以时间为条件，查询历史数据
# 以时间查询温度历史数据
@app.route('/data/wendu_time', methods=['POST'])
def wendu_time():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        start = request.values.get("start")
        end = request.values.get("end")
        db.ping(reconnect=True)
        cursor.execute("select wendu,wendu2,creat_time FROM data WHERE creat_time between '" +
                       start + "' and '" + end + "'")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["wendu"] = str(i[0])
                temp["wendu2"] = str(i[1])
                temp["creat_time"] = str(i[2])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 以时间查询电压历史数据
@app.route('/data/dianya_time', methods = ['POST'])
def dianya_time():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        start = request.values.get("start")
        end = request.values.get("end")
        db.ping(reconnect=True)
        cursor.execute("select dianya,dianya2,creat_time FROM data WHERE creat_time between '" +
                       start + "' and '" + end + "'")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["dianya"] = str(i[0])
                temp["dianya2"] = str(i[1])
                temp["creat_time"] = str(i[2])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 以时间查询电流历史数据
@app.route('/data/dianliu_time', methods = ['POST'])
def dianliu_time():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        start = request.values.get("start")
        end = request.values.get("end")
        db.ping(reconnect=True)
        cursor.execute("select dianliu,dianliu2,creat_time FROM data WHERE creat_time between '" +
                       start + "' and '" + end + "'")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["dianliu"] = str(i[0])
                temp["dianliu2"] = str(i[1])
                temp["creat_time"] = str(i[2])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 以时间查询转速历史数据
@app.route('/data/zhuansu_time', methods=['POST'])
def zhuansu_time():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        start = request.values.get("start")
        end = request.values.get("end")
        db.ping(reconnect=True)
        cursor.execute("select zhuansu,zhuansu2,creat_time FROM data WHERE creat_time between '" +
                       start + "' and '" + end + "'")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["zhuansu"] = str(i[0])
                temp["zhuansu2"] = str(i[1])
                temp["creat_time"] = str(i[2])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 以时间查询光照历史数据
@app.route('/data/guangzhao_time', methods=['POST'])
def guangzhao_time():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        start = request.values.get("start")
        end = request.values.get("end")
        db.ping(reconnect=True)
        cursor.execute("select guangzhao,guangzhao2,creat_time FROM data WHERE creat_time between '" +
                       start + "' and '" + end + "'")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["guangzhao"] = str(i[0])
                temp["guangzhao2"] = str(i[1])
                temp["creat_time"] = str(i[2])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 以时间查询经度历史数据
@app.route('/data/jingdu_time', methods=['POST'])
def jingdu_time():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        start = request.values.get("start")
        end = request.values.get("end")
        db.ping(reconnect=True)
        cursor.execute("select jingdu,jingdu2,creat_time FROM data WHERE creat_time between '" +
                       start + "' and '" + end + "'")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["jingdu"] = str(i[0])
                temp["jingdu2"] = str(i[1])
                temp["creat_time"] = str(i[2])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 以时间查询纬度历史数据
@app.route('/data/weidu_time', methods=['POST'])
def weidu_time():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        start = request.values.get("start")
        end = request.values.get("end")
        db.ping(reconnect=True)
        cursor.execute("select weidu,weidu2,creat_time FROM data WHERE creat_time between '" +
                       start + "' and '" + end + "'")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["weidu"] = str(i[0])
                temp["weidu2"] = str(i[1])
                temp["creat_time"] = str(i[2])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 以时间查询海拔历史数据
@app.route('/data/haiba_time', methods=['POST'])
def haiba_time():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        start = request.values.get("start")
        end = request.values.get("end")
        db.ping(reconnect=True)
        cursor.execute("select haiba,haiba2,creat_time FROM data WHERE creat_time between '" +
                       start + "' and '" + end + "'")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["haiba"] = str(i[0])
                temp["haiba2"] = str(i[1])
                temp["creat_time"] = str(i[2])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 以时间查询所有数据
@app.route('/check/all/creat_time', methods=['POST'])
def creat_time():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        start = request.values.get("start")
        end = request.values.get("end")
        db.ping(reconnect=True)
        cursor.execute("select ID1,ID2,wendu,wendu2,dianya,dianya2,zhuansu,zhuansu2,guangzhao,guangzhao2,jingdu,"
                       "jingdu2,weidu,weidu2,haiba,haiba2,creat_time FROM data WHERE creat_time between '" +
                       start + "' and '" + end + "'")
        data = cursor.fetchall()
        temp = {}
        result = []
        if (data != None):
            for i in data:
                temp["ID1"] = str(i[0])
                temp["ID2"] = str(i[1])
                temp["wendu"] = str(i[2])
                temp["wendu2"] = str(i[3])
                temp["dianya"] = str(i[4])
                temp["dianya2"] = str(i[5])
                temp["zhuansu"] = str(i[6])
                temp["zhuansu2"] = str(i[7])
                temp["guangzhao"] = str(i[8])
                temp["guangzhao2"] = str(i[9])
                temp["jingdu"] = str(i[10])
                temp["jingdu2"] = str(i[11])
                temp["weidu"] = str(i[12])
                temp["weidu2"] = str(i[13])
                temp["haiba"] = str(i[14])
                temp["haiba2"] = str(i[15])
                temp["creat_time"] = str(i[16])
                result.append(temp.copy())
            print("result:", data)
            print("result_length:", len(data))
            return jsonify(result)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify([])

# 更新阀值
# 更新温度阀值
@app.route('/data/update_temp', methods=['POST'])
def data_update_temp():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        wfazhigao = request.values.get("wfazhigao")
        wfazhidi = request.values.get("wfazhidi")
        try:
            db.ping(reconnect=True)
            cursor.execute("update threshold set wfazhigao=\"" + str(wfazhigao)
                           + "\",wfazhidi=\"" + str(wfazhidi) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return jsonify({"result": 1})
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return jsonify({"result": -1})

# 更新温度阀值2
@app.route('/data/update_temp2', methods=['POST'])
def data_update_temp2():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        wfazhigao2 = request.values.get("wfazhigao2")
        wfazhidi2 = request.values.get("wfazhidi2")
        try:
            db.ping(reconnect=True)
            cursor.execute("update threshold set wfazhigao2=\"" + str(wfazhigao2)
                           + "\",wfazhidi2=\"" + str(wfazhidi2) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return jsonify({"result": 1})
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return jsonify({"result": -1})

# 更新电压阀值
@app.route('/data/update_volt', methods=['POST'])
def data_update_volt():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        dfazhigao = request.values.get("dfazhigao")
        dfazhidi = request.values.get("dfazhidi")
        try:
            db.ping(reconnect=True)
            cursor.execute("update threshold set dfazhigao=\"" + str(dfazhigao)
                           + "\",dfazhidi=\"" + str(dfazhidi) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return jsonify({"result": 1})
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return jsonify({"result": -1})

# 更新电压阀值2
@app.route('/data/update_volt2', methods=['POST'])
def data_update_volt2():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        dfazhigao2 = request.values.get("dfazhigao2")
        dfazhidi2 = request.values.get("dfazhidi2")
        try:
            db.ping(reconnect=True)
            cursor.execute("update threshold set dfazhigao2=\"" + str(dfazhigao2)
                           + "\",dfazhidi2=\"" + str(dfazhidi2) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return jsonify({"result": 1})
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return jsonify({"result": -1})

# 更新转速阀值
@app.route('/data/update_rev', methods=['POST'])
def data_update_rev():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        zfazhigao = request.values.get("zfazhigao")
        zfazhidi = request.values.get("zfazhidi")
        try:
            db.ping(reconnect=True)
            cursor.execute("update threshold set zfazhigao=\"" + str(zfazhigao)
                           + "\",zfazhidi=\"" + str(zfazhidi) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return jsonify({"result": 1})
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return jsonify({"result": -1})

# 更新转速阀值2
@app.route('/data/update_rev2', methods=['POST'])
def data_update_rev2():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        zfazhigao2 = request.values.get("zfazhigao2")
        zfazhidi2 = request.values.get("zfazhidi2")
        try:
            db.ping(reconnect=True)
            cursor.execute("update threshold set zfazhigao2=\"" + str(zfazhigao2)
                           + "\",zfazhidi2=\"" + str(zfazhidi2) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return jsonify({"result": 1})
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return jsonify({"result": -1})

# 更新光照阀值
@app.route('/data/update_lux', methods=['POST'])
def data_update_lux():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        gfazhigao = request.values.get("gfazhigao")
        gfazhidi = request.values.get("gfazhidi")
        try:
            db.ping(reconnect=True)
            cursor.execute("update threshold set gfazhigao=\"" + str(gfazhigao)
                           + "\",gfazhidi=\"" + str(gfazhidi) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return jsonify({"result": 1})
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return jsonify({"result": -1})

# 更新光照阀值2
@app.route('/data/update_lux2', methods=['POST'])
def data_update_lux2():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        gfazhigao2 = request.values.get("gfazhigao2")
        gfazhidi2 = request.values.get("gfazhidi2")
        try:
            db.ping(reconnect=True)
            cursor.execute("update threshold set gfazhigao2=\"" + str(gfazhigao2)
                           + "\",gfazhidi2=\"" + str(gfazhidi2) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return jsonify({"result": 1})
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return jsonify({"result": -1})


# 更新单个阀值
# 更新温度一高阀值
@app.route('/data/update_wfazhigao', methods=['POST'])
def data_update_wfazhigao():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        wfazhigao = request.values.get("wfazhigao")
        try:
            cursor.execute("update threshold set wfazhigao=\"" + str(wfazhigao) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新温度二高阀值
@app.route('/data/update_wfazhigao2', methods=['POST'])
def data_update_wfazhigao2():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        wfazhigao2 = request.values.get("wfazhigao2")
        try:
            cursor.execute("update threshold set wfazhigao2=\"" + str(wfazhigao2) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新温度一低阀值
@app.route('/data/update_wfazhidi', methods=['POST'])
def data_update_wfazhidi():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        wfazhidi = request.values.get("wfazhidi")
        try:
            cursor.execute("update threshold set wfazhidi=\"" + str(wfazhidi) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新温度二低阀值
@app.route('/data/update_wfazhidi2', methods=['POST'])
def data_update_wfazhidi2():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        wfazhidi2 = request.values.get("wfazhidi2")
        try:
            cursor.execute("update threshold set wfazhidi2=\"" + str(wfazhidi2) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新电压一高阀值
@app.route('/data/update_dfazhigao', methods=['POST'])
def data_update_dfazhigao():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        dfazhigao = request.values.get("dfazhigao")
        try:
            cursor.execute("update threshold set dfazhigao=\"" + str(dfazhigao) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新电压二高阀值
@app.route('/data/update_dfazhigao2', methods=['POST'])
def data_update_dfazhigao2():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        dfazhigao2 = request.values.get("dfazhigao2")
        try:
            cursor.execute("update threshold set dfazhigao2=\"" + str(dfazhigao2) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新电压一低阀值
@app.route('/data/update_dfazhidi', methods=['POST'])
def data_update_dfazhidi():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        dfazhidi = request.values.get("dfazhidi")
        try:
            cursor.execute("update threshold set dfazhidi=\"" + str(dfazhidi) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新电压二低阀值
@app.route('/data/update_dfazhidi2', methods=['POST'])
def data_update_dfazhidi2():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        dfazhidi2 = request.values.get("dfazhidi2")
        try:
            cursor.execute("update threshold set dfazhidi2=\"" + str(dfazhidi2) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新转速一高阀值
@app.route('/data/update_zfazhigao', methods=['POST'])
def data_update_zfazhigao():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        zfazhigao = request.values.get("zfazhigao")
        try:
            cursor.execute("update threshold set zfazhigao=\"" + str(zfazhigao) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新转速二高阀值
@app.route('/data/update_zfazhigao2', methods=['POST'])
def data_update_zfazhigao2():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        zfazhigao2 = request.values.get("zfazhigao2")
        try:
            cursor.execute("update threshold set zfazhigao2=\"" + str(zfazhigao2) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新转速一低阀值
@app.route('/data/update_zfazhidi', methods=['POST'])
def data_update_zfazhidi():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        zfazhidi = request.values.get("zfazhidi")
        try:
            cursor.execute("update threshold set zfazhidi=\"" + str(zfazhidi) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新转速二低阀值
@app.route('/data/update_zfazhidi2', methods=['POST'])
def data_update_zfazhidi2():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        zfazhidi2 = request.values.get("zfazhidi2")
        try:
            cursor.execute("update threshold set zfazhidi2=\"" + str(zfazhidi2) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新光照一高阀值
@app.route('/data/update_gfazhigao', methods=['POST'])
def data_update_gfazhigao():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        gfazhigao = request.values.get("gfazhigao")
        try:
            cursor.execute("update threshold set gfazhigao=\"" + str(gfazhigao) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新光照二高阀值
@app.route('/data/update_gfazhigao2', methods=['POST'])
def data_update_gfazhigao2():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        gfazhigao2 = request.values.get("gfazhigao2")
        try:
            cursor.execute("update threshold set gfazhigao2=\"" + str(gfazhigao2) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新光照一低阀值
@app.route('/data/update_gfazhidi', methods=['POST'])
def data_update_gfazhidi():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        gfazhidi = request.values.get("gfazhidi")
        try:
            cursor.execute("update threshold set gfazhidi=\"" + str(gfazhidi) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新光照二低阀值
@app.route('/data/update_gfazhidi2', methods=['POST'])
def data_update_gfazhidi2():
    db = reconnect()
    cursor = db.cursor()
    global isChange
    if request.method == "POST":
        gfazhidi2 = request.values.get("gfazhidi2")
        try:
            cursor.execute("update threshold set gfazhidi2=\"" + str(gfazhidi2) + "\"")
            db.commit()
            print("update data successfully!")
            isChange = True
            return "1"
        except Exception as e:
            print("update data failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 查询所有阀值
@app.route('/data/check_all_threshold', methods=['POST'])
def data_check_all_threshold():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select * from threshold")
        data = cursor.fetchone()
        print(data)
        temp = {}
        if (data != None):
            temp = {
                "wfazhigao": data[1],
                "wfazhidi": data[2],
                "dfazhigao": data[3],
                "dfazhidi": data[4],
                "zfazhigao": data[5],
                "zfazhidi": data[6],
                "gfazhigao": data[7],
                "gfazhidi": data[8],
                "wfazhigao2": data[9],
                "wfazhidi2": data[10],
                "dfazhigao2": data[11],
                "dfazhidi2": data[12],
                "zfazhigao2": data[13],
                "zfazhidi2": data[14],
                "gfazhigao2": data[15],
                "gfazhidi2": data[16]
            }
            print("result:", temp)
            return jsonify(temp)
        else:
            print("result: NULL")
            return jsonify([])


# 查询温度上下限
@app.route('/data/check_wfazhiall', methods=['POST'])
def data_check_wfazhiall():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select wfazhigao,wfazhidi from threshold")   # creat_time
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"wfazhigao": str(data[0]), "wfazhidi": str(data[1])}   # "creat_time": str(data[2])
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 查询温度2上下限
@app.route('/data/check_wfazhiall2', methods=['POST'])
def data_check_wfazhiall2():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select wfazhigao2,wfazhidi2 from threshold")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"wfazhigao2": str(data[0]), "wfazhidi2": str(data[1])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 查询电压上下限
@app.route('/data/check_dfazhiall', methods=['POST'])
def data_check_dfazhiall():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select dfazhigao,dfazhidi from threshold")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"dfazhigao": str(data[0]), "dfazhidi": str(data[1])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 查询电压2上下限
@app.route('/data/check_dfazhiall2', methods=['POST'])
def data_check_dfazhiall2():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select dfazhigao2,dfazhidi2 from threshold")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"dfazhigao2": str(data[0]), "dfazhidi2": str(data[1])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 查询转速上下限
@app.route('/data/check_zfazhiall', methods=['POST'])
def data_check_zfazhiall():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select zfazhigao,zfazhidi from threshold")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"zfazhigao": str(data[0]), "zfazhidi": str(data[1])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 查询转速2上下限
@app.route('/data/check_zfazhiall2', methods=['POST'])
def data_check_zfazhiall2():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select zfazhigao2,zfazhidi2 from threshold")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"zfazhigao2": str(data[0]), "zfazhidi2": str(data[1])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 查询光照上下限
@app.route('/data/check_gfazhiall', methods=['POST'])
def data_check_gfazhiall():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select gfazhigao,gfazhidi from threshold")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"gfazhigao": str(data[0]), "gfazhidi": str(data[1])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 查询光照上下限
@app.route('/data/check_gfazhiall2', methods=['POST'])
def data_check_gfazhiall2():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select gfazhigao2,gfazhidi2 from threshold")
        data = cursor.fetchone()
        if (data != None):
            print("result:", data)
            jsondata = {"gfazhigao2": str(data[0]), "gfazhidi2": str(data[1])}
            return jsonify(jsondata)
        else:
            print("result:NULL")
            jsondata = {}
            return jsonify(jsondata)

# 更新状态开关数据
@app.route('/state_mylight', methods=['POST'])
def state_mylight():
    db = reconnect()
    cursor = db.cursor()
    global LightChange
    if request.method == "POST":
        light = request.values.get("light")
        try:
            cursor.execute("update state set light=\"" + str(light) + "\"")
            db.commit()  # 提交，使操作生效
            print("update successfully!")
            LightChange = True
            return jsonify({"result": light})
        except Exception as e:
            print("update failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新风扇状态
@app.route('/state_fan', methods=['POST'])
def state_fan():
    db = reconnect()
    cursor = db.cursor()
    global FanChange
    if request.method == "POST":
        fan = request.values.get("fan")
        try:
            cursor.execute("update state set fan=\"" + str(fan) + "\"")
            db.commit()  # 提交，使操作生效
            print("update state_fan successfully!")
            FanChange = True
            return jsonify({"result": fan})
        except Exception as e:
            print("update state_fan failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新风扇2状态
@app.route('/state_twofan', methods=['POST'])
def state_twofan():
    db = reconnect()
    cursor = db.cursor()
    global TwofanChange
    if request.method == "POST":
        twofan = request.values.get("twofan")
        try:
            cursor.execute("update state set fan2=\"" + str(twofan) + "\"")
            db.commit()  # 提交，使操作生效
            print("update successfully!")
            TwofanChange = True
            return jsonify({"result": twofan})
        except Exception as e:
            print("update failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新电机状态
@app.route('/state_elce', methods=['POST'])
def state_elce():
    db = reconnect()
    cursor = db.cursor()
    global ElceChange
    if request.method == "POST":
        elce = request.values.get("elce")
        try:
            cursor.execute("update state set elce=\"" + str(elce) + "\"")
            db.commit()  # 提交，使操作生效
            print("update successfully!")
            ElceChange = True
            return jsonify({"result": elce})
        except Exception as e:
            print("update failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新转速
@app.route('/state/update_speed', methods=['POST'])
def state_update_speed():
    db = reconnect()
    cursor = db.cursor()
    global revChange
    if request.method == "POST":
        print(request.values)
        speed = request.values.get("speed")
        try:
            db.ping(reconnect=True)
            cursor.execute("update state set speed=\"" + str(speed) + "\" where 1 order by id desc limit 1")
            db.commit()
            print("update successfully!")
            revChange = True
            print(revChange)
            return "1"
        except Exception as e:
            print("update failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 更新转速2
@app.route('/state/update_speed2', methods=['POST'])
def state_update_speed2():
    db = reconnect()
    cursor = db.cursor()
    global trevChange
    if request.method == "POST":
        print(request.values)
        speed2 = request.values.get("speed2")
        try:
            db.ping(reconnect=True)
            cursor.execute("update state set speed2=\"" + str(speed2) + "\" where 1 order by id desc limit 1")
            db.commit()
            print("update successfully!")
            trevChange = True
            print(trevChange)
            return "1"
        except Exception as e:
            print("update failed:", e)
            db.rollback()  # 发生错误就回滚
            return "-1"

# 查询所有状态数据
@app.route('/state_all', methods=['POST'])
def state_all():
    db = reconnect()
    cursor = db.cursor()
    if request.method == "POST":
        db.ping(reconnect=True)
        cursor.execute("select * from state")
        data = cursor.fetchone()
        print(data)
        temp = {}
        if (data != None):
            temp = {
                "light": data[1],
                "fan": data[2],
                "twofan": data[3],
                "elce": data[4],
            }
            print("result:", temp)
            return jsonify(temp)
        else:
            print("result: NULL")
            return jsonify([])

# ,,
if __name__ == "__main__":
    t1 = threading.Thread(target=hhhh)
    # t2 = threading.Thread(target=connect_reset)
    t1.start()
    # t2.start()
    # app.run(host='192.168.100.145', port=9000)
    app.run(host='0.0.0.0', port=9000)
    db = reconnect()
    db.close()
    print("Good bye!")
