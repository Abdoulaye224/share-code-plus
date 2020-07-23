#!/usr/bin/env python3
import os
import socket
import sqlite3
from itertools import chain
from random import choice
from string import ascii_letters, digits

from flask import request
from win32timezone import now


def create_uid_sqlite(n=9):
   '''Génère une chaîne de caractères alétoires de longueur n
   en évitant 0, O, I, l pour être sympa.'''
   chrs = [ c for c in chain(ascii_letters,digits)
                        if c not in '0OIl'  ]
   return ''.join( ( choice(chrs) for i in range(n) ) )

def save_doc_as_file_sqlite(uid=None, code=None, langage=None):
    '''Crée/Enregistre le document sous la forme d'un fichier
    data/uid. Return the file name.
    '''
    null = None
    date_time = now()
    cmd = request.user_agent.browser
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)

    if uid is None:
        uid = create_uid_sqlite()
        code = '# Write your code here...'
        langage = ''

        connection = sqlite3.connect('tp.db')
        cursor = connection.cursor()
        cursor.execute("INSERT INTO SHARECODE VALUES(?, ?, ?)", (uid, code, langage))
        cursor.execute("INSERT INTO USER VALUES(?, ?, ?, ?, ?)", (null, uid, IPAddr, cmd, date_time))
        connection.commit()
        connection.close()
    connection = sqlite3.connect('tp.db')
    cursor1 = connection.cursor()
    cursor1.execute('''UPDATE SHARECODE SET code = ?, langage = ? WHERE uid = ? ''', (code, langage, uid))
    cursor1.execute(
        '''UPDATE USER SET timestamp = ?, Ip = ?, navigator = ?  WHERE uid = ? ''',
        (date_time, IPAddr, cmd, uid))
    connection.commit()
    connection.close()
    with open('data/{}'.format(uid),'w') as fd:
        fd.write(code)
    with open('data/{}'.format(uid + '.lang'), 'w') as fd:
        fd.write(langage)
    return uid

def read_doc_as_file_sqlite(uid):
    '''Lit le document data/uid'''
    try:
        with open('data/{}'.format(uid)) as fd:
            code = fd.read()
        return code
    except FileNotFoundError:
        return None

def get_last_entries_from_files_sqlite(n=10, nlines=10):
    entries = os.scandir('data')
    d = []
    entries = sorted(list(entries),
                     key=(lambda e: e.stat().st_mtime),
                     reverse=True)
    for i,e in enumerate(entries):
        if i >= n:
            break
        if e.name.startswith('.'):
            continue
        with open('data/{}'.format(e.name)) as fd:
            code = ''.join(( fd.readline() for i in range(nlines) ))
            if fd.readline():
                code += '\n...'
        d.append({ 'uid':e.name, 'code':code })
    return d

def get_last_entries_from_files_admin_sqlite(n=10, nlines=10):
    entries = os.scandir('data')
    d = []
    user = ""
    entries = sorted(list(entries),
                     key=(lambda e: e.stat().st_mtime),
                     reverse=True)
    for i, e in enumerate(entries):
        if i >= n:
            break
        if '.lang' in e.name:
            continue
        with open('data/{}'.format(e.name)) as fd:
            code = ''.join((fd.readline() for i in range(nlines)))
            if fd.readline():
                code += '\n...'
        uid = str(e.name)
        print(uid)
        connection = sqlite3.connect('tp.db')
        cursor1 = connection.cursor()
        ip = cursor1.execute('''SELECT Ip FROM USER where uid = ? ''', (uid,));
        ip = ip.fetchone()
        navigator = cursor1.execute('''SELECT navigator FROM USER where uid = ? ''', (uid,));
        navigator = navigator.fetchone()
        timestamp = cursor1.execute('''SELECT timestamp FROM USER where uid = ? ''', (uid,));
        timestamp = timestamp.fetchone()
        print(user)
        connection.commit()
        connection.close()
        d.append({'uid': e.name, 'code': code, 'ip': ip, 'navigator': navigator, 'timestamp': timestamp,})
    print(user)
    return d

