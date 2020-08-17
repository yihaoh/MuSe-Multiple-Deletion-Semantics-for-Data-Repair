from flask import Flask, render_template, url_for, request, redirect, jsonify
import json
import os
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from flask_login import current_user, login_required

import sys

from app.main.database_generator.dba import *
from app.main.Semantics.independent_sem import IndependentSemantics
from app.main.Semantics.end_sem import EndSemantics
from app.main.Semantics.step_sem import StepSemantics
from app.main.Semantics.stage_sem import StageSemantics

from app.main import bp

# ============================ Define Schema ======================== #
mas_schema = {
    "author": ['aid', 'name', 'oid'],
    "publication": ['pid', 'title', 'year'],
    "writes": ['aid', 'pid'],
    "organization": ['oid', 'name'],
    "cite": ['citing', 'cited']
}
# mas_schema = {
#     "grants": "(gid, name)",
#     "authgrant": "(aid, gid)",
#     "author": "(aid, name)",
#     "cite": "(citing, cited)",
#     "writes": "(aid, pid)",
#     "pub": "(pid, title)"
# }


# =========================== Actual Implementation ==============================

# input screen
# @bp.route('/', methods=['POST', 'GET'])
@bp.route('/input', methods=['POST', 'GET'])
@login_required
def input():
    mydb = current_user.username

    # get tables
    conn = psycopg2.connect(database=mydb, user="postgres", password="123", host="localhost", port="5432")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # delete the db used for derivation
    cur.execute('DROP DATABASE IF EXISTS ' + mydb + '1;')
    conn.commit()

    # table stats
    cur.execute('SELECT relname,n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC;')
    tableStat = [i for i in cur.fetchall() if 'delta' not in i[0]]

    cur.close()
    conn.close()

    # Construct Example here
    semantics = ['Independent', 'Step', 'Stage', "End"]

    # load JSON graph
    graph = json.load(open(os.getcwd() + "/ex2.json"))

    # print(request.form)
    return render_template('main/input.html', available_tables=tableStat,
                           table_schemas=mas_schema, semantics=semantics,
                           graph=graph, user=current_user)


# output screen
@bp.route('/results', methods=['POST', 'GET'])
@login_required
def output():
    tables = ['author', 'publication', 'writes', 'organization', 'cite']

    if request.method == 'GET':
        return redirect(url_for('main.input'))

    mydb = current_user.username
    delta_db = mydb + '1'

    conn = psycopg2.connect(database=mydb, user="postgres", password="123", host="localhost", port="5432")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    deleted = {}
    visualization = {}

    # selected semantic
    s = request.form['semantic-selection']

    print(request.form)

    # parse all rules
    rules = []
    r, n = 'Rule-', 1
    ruleNum = r + str(n)
    while ruleNum in request.form:
        tp = request.form[ruleNum]
        rules.append((tp.split(' ')[3], tp[(tp.find('(') + 1):-2] + ';'))
        n += 1
        ruleNum = r + str(n)

    print(rules)

    # Make a duplicate of the database
    cur.execute('CREATE DATABASE ' + delta_db + ' WITH TEMPLATE ' + mydb + ';')
    conn.commit()

    db = DatabaseEngine(delta_db)

    # different semantics
    if s == 'Independent':
        print('Independent Semantic')
        ind_sem = IndependentSemantics(db, rules, tables)
        mss, visualization[s], _ = ind_sem.find_mss(mas_schema)

        res = {}
        for record in mss:
            if record[0] not in res:
                res[record[0]] = []
                res[record[0]].append(['#'] + mas_schema[record[0]])
            res[record[0]].append(record[1][1:-1].split(','))

        # print(mss)

        deleted['Independent'] = res
        # table: list of tuples
        # deleted['Independent'] = {  'Found': [['fid', 'name'], [2, 'ERC']],
        #                             'AuthGrant': [['aid', 'fid'], [4, 2], [5, 2]], 
        #                         }

    elif s == 'Step':
        print('Step Semantic')
        step = StepSemantics(db, rules, tables)
        mss, visualization[s], _ = step.find_mss(mas_schema)
        res = []
        dedup = set()
        for record in mss:
            if record not in dedup:
                dedup.add(record)
                res.append([record[0], ['#'] + mas_schema[record[0]], list(record[1])])

        deleted['Step'] = res

        # list of [table, schema, list of tuples and rule]
        # deleted['Step'] = [ ['Found', ['fid', 'name'], [2, 'ERC', 0]], 
        #                     ['Author', ['aid', 'name'], [4, 'Marge', 1]], 
        #                     ['Author', ['aid', 'name'], [5, 'Homer', 1]],
        #                     ['Writes', ['aid', 'pid'], [4, 6, 3]], 
        #                     ['Writes', ['aid', 'pid'], [5, 7, 3]] ]

    elif s == 'Stage':
        print('Stage Semantic')
        stage = StageSemantics(db, rules, tables)
        mss, visualization[s], _ = stage.find_mss()
        res = []

        for ms in mss:
            if len(ms) == 0:
                break

            tp = []  # list of [table, schema, tuple...]
            d = {}
            # store tuples in map
            for record in ms:
                if record[0] not in d:
                    d[record[0]] = []
                d[record[0]].append([record[1], record[2]])

            # format the list
            for key, val in d.items():
                sub = []  # table, schema, tuples...
                sub.append(key)
                sub.append(['#'] + mas_schema[key])
                for r in val:
                    sub.append(r)

                tp.append(sub)

            # add stage to res
            res.append(tp)

        deleted['Stage'] = res
        # list of [table, list of deleted tuples]
        # deleted['Stage'] = [    [['Found', ['fid', 'name'], [2, 'ERC', 0]]], 
        #                         [['Author', ['aid', 'name'], [4, 'Marge', 1], [5, 'Homer', 1]]], 
        #                         [['Writes', ['aid', 'pid'], [4, 6, 3], [5, 7, 3]], ['Pub', ['pid', 'title'], [6, 'x', 2], [7, 'y', 2]]]
        #                     ]

    else:  # s == 'End'
        print('End Semantic')
        end_sem = EndSemantics(db, rules, tables)
        mss, visualization[s], _ = end_sem.find_mss()
        res = {}
        for record in mss:
            if record[0] not in res:
                res[record[0]] = []
                res[record[0]].append(['#'] + mas_schema[record[0]])
            res[record[0]].append(list(record[1]))

        deleted['End'] = res

        # same as independent
        # deleted['End'] = {  'Found': [['fid', 'name'], [2, 'ERC']],
        #                     'Author': [['aid', 'name'], [4, 'Marge'], [5, 'Homer']], 
        #                     'Writes': [['aid', 'pid'], [4, 6], [5, 7]], 
        #                     'Pub': [['pid', 'title'], [6, 'x'], [7, 'y']], 
        #                     'Cite': [['citing', 'cited'], [7, 6]] }
    db.close_connection()
    del db

    # get tables
    # conn.commit()
    cur.execute('SELECT relname,n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC;')
    tables = [i for i in cur.fetchall() if 'delta' not in i[0]]

    cur.close()
    conn.close()

    return render_template('main/results.html', semantic=json.dumps(s),
                           rules=rules,
                           available_tables=tables,
                           table_schemas=mas_schema,
                           deleted=json.dumps(deleted[s]),
                           visual=json.dumps(visualization[s]),
                           user=current_user)


# sql to explore db
@bp.route('/query', methods=['POST'])
@login_required
def sqlQuery():
    sql = request.form['query']
    result = {}

    banned = ['DELETE', 'UPDATE', 'INSERT', 'CREATE', 'DROP']
    if any(x in sql.upper() for x in banned):
        result['error'] = 'Only SELECT query is allowed'
        return jsonify(render_template('main/query.html', res=result))

    mydb = current_user.username

    conn = psycopg2.connect(database=mydb, user="postgres", password="123", host="localhost", port="5432")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    try:
        cur.execute(sql)
        result['attrs'] = [i[0] for i in cur.description]
        result['rows'] = cur.fetchall()
        # print(result['attrs'])
        # print(result['rows'])
    except:
        result['error'] = 'Query execution failed, please check your query!'
        print('Error in SQL Query!')

    conn.commit()
    cur.close()
    conn.close()
    return jsonify(render_template('main/query.html', res=result))


# restore the database
@bp.route('/restore', methods=['POST', 'GET'])
@login_required
def restore():
    tables = ['author', 'publication', 'writes', 'organization', 'cite']

    # loadDB(current_user.username)
    # get the table names for reload
    mydb = current_user.username

    # reload the database
    db = DatabaseEngine(mydb)
    db.delete_tables(tables)
    db.load_database_tables(tables)
    del db

    return redirect(url_for('main.input'))


# commit the change
@bp.route('/commit', methods=['POST'])
@login_required
def commitChange():
    print('commit changes!!!!!!!!!')
    for i in request.form:
        data = json.loads(i)
        del_tuples(data)

    result = {'url': url_for('main.input')}
    return jsonify(result)


# preview
@bp.route('/preview', methods=['POST'])
@login_required
def preview():
    tables = ['author', 'publication', 'writes', 'organization', 'cite']
    mydb = current_user.username
    delta_db = mydb + '1'

    conn = psycopg2.connect(database=mydb, user="postgres", password="123", host="localhost", port="5432")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute('DROP DATABASE IF EXISTS ' + delta_db + ';')
    conn.commit()

    rules = []
    for r in request.json['rules']:
        rules.append((r.split(' ')[3], r[(r.find('(') + 1):-2] + ';'))

    if len(rules) == 0:
        return ''

    stats = {}

    cur.execute('CREATE DATABASE ' + delta_db + ' WITH TEMPLATE ' + mydb + ';')
    conn.commit()
    db = DatabaseEngine(delta_db)
    ind_sem = IndependentSemantics(db, rules, tables)
    _, _, stats['independent'] = ind_sem.find_mss(mas_schema)
    db.close_connection()
    del db
    cur.execute('DROP DATABASE IF EXISTS ' + delta_db + ';')
    conn.commit()

    cur.execute('CREATE DATABASE ' + delta_db + ' WITH TEMPLATE ' + mydb + ';')
    conn.commit()
    db = DatabaseEngine(delta_db)
    step = StepSemantics(db, rules, tables)
    _, _, stats['step'] = step.find_mss(mas_schema)
    db.close_connection()
    del db
    cur.execute('DROP DATABASE IF EXISTS ' + delta_db + ';')
    conn.commit()

    cur.execute('CREATE DATABASE ' + delta_db + ' WITH TEMPLATE ' + mydb + ';')
    conn.commit()
    db = DatabaseEngine(delta_db)
    stage = StageSemantics(db, rules, tables)
    _, _, stats['stage'] = stage.find_mss()
    db.close_connection()
    del db
    cur.execute('DROP DATABASE IF EXISTS ' + delta_db + ';')
    conn.commit()

    cur.execute('CREATE DATABASE ' + delta_db + ' WITH TEMPLATE ' + mydb + ';')
    conn.commit()
    db = DatabaseEngine(delta_db)
    end_sem = EndSemantics(db, rules, tables)
    _, _, stats['end'] = end_sem.find_mss()
    db.close_connection()
    del db
    cur.execute('DROP DATABASE IF EXISTS ' + delta_db + ';')
    conn.commit()

    cur.close()
    conn.close()
    return jsonify(render_template('main/preview.html', stats=stats))



# delete tuples in ORIGINAL database
def del_tuples(data):
    mydb = current_user.username
    conn = psycopg2.connect(database=mydb, user="postgres", password="123", host="localhost", port="5432")
    # conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    try:
        for key, val in data.items():
            attrs = val[0]

            query = "DELETE FROM " + key + " WHERE "
            for i in range(len(attrs)):
                if i > 0:
                    query += attrs[i] + "=%s"
                    query += " AND " if i < len(attrs) - 1 else ";"

            # print(query)
            for t in val[1]:
                cur.execute(query, tuple(t[1:]))
                conn.commit()
        cur.close()
        conn.close()
    except:
        print('Error query!')
        cur.close()
        conn.close()


# reload all tables in database
def loadDB(dbname):
    print('restoring all tables')
    tables = ['author', 'publication', 'writes', 'organization', 'cite']
    db = DatabaseEngine(dbname)
    db.delete_tables(tables)
    db.load_database_tables(tables)
    del db
    # cur = conn.cursor()
    # cur.execute('''DROP DATABASE IF EXIST cr;''')
    # cur.commit()
    # cur.execute('''CREATE DATABASE cr;''')
    # create_queries_prov1 = [
    #         'CREATE TABLE Delta_author (aid int, name varchar(60), oid int);',
    #         'CREATE TABLE Delta_publication (pid int, title varchar(200), year int);',
    #         'CREATE TABLE Delta_writes (aid int, pid int);',
    #         'CREATE TABLE Delta_cite (citing int, cited int);',
    #         'CREATE TABLE Delta_organization (oid int, name varchar(150));'
    #     ]
    # create_queries_prov2 = [
    #         'CREATE TABLE author (aid int, name varchar(60), oid int);',
    #         'CREATE TABLE publication (pid int, title varchar(200), year int);',
    #         'CREATE TABLE writes (aid int, pid int);',
    #         'CREATE TABLE cite (citing int, cited int);',
    #         'CREATE TABLE organization (oid int, name varchar(150));'
    #     ]
    #   CREATE TABLE delta_grants (gid int, name varchar(60));
    #   CREATE TABLE delta_authgrant (aid int, gid int);
    #   CREATE TABLE delta_author (aid int, name varchar(60));
    #   CREATE TABLE delta_cite (citing int, cited int);
    #   CREATE TABLE delta_writes (aid int, pid int);
    #   CREATE TABLE delta_pub (pid int, title varchar(150));

    #   CREATE TABLE grants (gid int, name varchar(60));
    #   CREATE TABLE authgrant (aid int, gid int);
    #   CREATE TABLE author (aid int, name varchar(60));
    #   CREATE TABLE cite (citing int, cited int);
    #   CREATE TABLE writes (aid int, pid int);
    #   CREATE TABLE pub (pid int, title varchar(150));
