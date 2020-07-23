import sqlite3
import socket
from flask import Flask, request, render_template, \
                  redirect

from model_sqlite import save_doc_as_file_sqlite, \
                  read_doc_as_file_sqlite, \
                  get_last_entries_from_files_sqlite

from flask import request
from win32timezone import now

connection = sqlite3.connect('tp.db')
connection2 = sqlite3.connect('user.db')

cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS SHARECODE(uid CHAR(50) PRIMARY KEY, code text, langage CHAR(50))')
connection.commit()
connection.close()

cursor2 = connection2.cursor()
cursor2.execute('CREATE TABLE IF NOT EXISTS USER(id INTEGER PRIMARY KEY, uid CHAR(50), Ip CHAR(50), navigator CHAR(50), timestamp CHAR(50))')
connection2.commit()
connection2.close()

#cursor.execute("INSERT INTO SHARECODE VALUES('1', 'test', 'test')")

app = Flask(__name__)

@app.route('/')
def index():
    #d = { 'last_added':[ { 'uid':'testuid', 'code':'testcode' } ] }
    d = { 'last_added':get_last_entries_from_files_sqlite() }
    return render_template('index.html',**d)

@app.route('/create')
def create():
    uid = save_doc_as_file_sqlite()
    return redirect("{}edit/{}".format(request.host_url,uid))

@app.route('/edit/<string:uid>/')
def edit(uid):
    code = read_doc_as_file_sqlite(uid)
    if code is None:
        return render_template('error.html',uid=uid)
    d = dict( uid=uid, code=code,
              url="{}view/{}".format(request.host_url,uid))
    return render_template('edit.html', **d)

@app.route('/publish',methods=['POST'])
def publish():
    code = request.form['code']
    uid  = request.form['uid']
    langage = request.form['langage']
    null = None
    date_time = now()
    cmd = request.user_agent.browser
    connection = sqlite3.connect('tp.db')
    connection2 = sqlite3.connect('user.db')
    cursor = connection.cursor()
    cursor2 = connection2.cursor()
    cursor.execute("INSERT INTO SHARECODE VALUES(?, ?, ?)", (uid, code, langage))
    connection.commit()
    connection.close()

    save_doc_as_file_sqlite(uid,code,langage)
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    print("Your Computer Name is:" + hostname)
    print("Your Computer IP Address is:" + IPAddr)
    print("Your browser is:" + cmd)

    cursor2.execute("INSERT INTO USER VALUES(?, ?, ?, ?, ?)", (null, uid, IPAddr, cmd, date_time))
    connection2.commit()
    connection2.close()
    return redirect("{}{}/{}".format(request.host_url,
                                     request.form['submit'],
                                     uid))

@app.route('/view/<string:uid>/')
def view(uid):
    code = read_doc_as_file_sqlite(uid)
    if code is None:
        return render_template('error.html',uid=uid)
    d = dict( uid=uid, code=code,
              url="{}view/{}".format(request.host_url,uid))
    return render_template('view.html', **d)

@app.route('/admin/')
def admin():
    pass

if __name__ == '__main__':
    app.run()

