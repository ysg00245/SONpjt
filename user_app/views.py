<<<<<<< HEAD
#1111

=======
#5555 Test Modify from inmost
#4444 Test Modify from inmost
#3333 Test Modify from inmost
#2222 Test Modify from inmost
#1111 
>>>>>>> 23d030d061030c7a49bf99129f3bd8e32071b7eb
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#from django.shortcuts import render

#from http.client import responses
from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt

import pymysql, json, random, string

def null(request) :
    return HttpResponse('Null Page..')

@csrf_exempt
def login(request) :
    # Conn부분을 함수내에 입력하지 않을경우 세션연결 이슈가 있음..
    # 별도 모듈을 만들어서 옮겨서 사용해도 문제없을지 확인필요..
    conn = pymysql.connect(host="27.96.130.7", port=3306, user="root", password="!Qpp041096", db="djangotest", charset="utf8")
    curs = conn.cursor(pymysql.cursors.DictCursor)

    uid = request.GET.get('uid')
    nick = request.GET.get('nick')
    ssid = request.GET.get('ssid')
    uuid = request.GET.get('uuid')

    if uid == '' or uid is None :
        return HttpResponse("유저고유ID(UID)는 필수 입력값입니다.")
    if nick == '' or nick is None :
        if request.method == 'POST' :
            return HttpResponse("닉네임(NICK)은 필수 입력값입니다.")
    # 클라에서 기본적으로 신규유저, 기존유저를 체크해서..
    # 신규유저면 POST.., 기존유저면 GET으로 요청을 한다는 조건하에.. 아래의 로직을 생성.
    if ssid == '' or ssid is None :
        if request.method == 'GET' :
            ssid = 100

    ss_num = number = "".join([random.choice(string.ascii_letters) for _ in range(15)])

    ssid_rtn = {
        "ss_id" : ss_num
    }

    if request.method == 'GET' :

        sql = "select uid, nick, lv, exp, gem, gold, stamina, char_cnt, skill_cnt, ss_id, state, play_time, DATE_FORMAT(last_dt, '%%Y%%m%%d') last_dt FROM zu_user_info WHERE uid = %s ORDER BY last_dt"
        curs.execute(sql, uid)
        rows = curs.fetchone()
        
        if rows :
            ss_id_chk = rows["ss_id"]
            # SSID 체크로직이 명확하지않아.. 우선은 주석처리함.
            #if ssid == int(100) :
            #    print("최초접속")
            #elif int(ss_id_chk) == int(ssid) :
            #    print("동일기기 확인.. Ok")
            #else :
            #    print("다른 기기 접속.. Err")
            #    err_msg = '''기존 SS_ID [{}]와 현재 SS_ID [{}]의 값이 상이하여 접속을 차단합니다.
            #    '''
            #    err_msg = err_msg.format(ss_id_chk, ssid)
            #    return HttpResponse(err_msg)

            sql2 = "update zu_user_info set ss_id=%s where uid=%s"
            curs.execute(sql2, (ss_num, uid))
            conn.commit()
            conn.close()
            ssid_rtn = json.dumps(ssid_rtn)
            data = json.dumps(rows)
            return HttpResponse((ssid_rtn, data))
        else :
            conn.close()

            err_msg = '''uid : {}는 존재하지 않는 데이터입니다."'''
            err_msg = err_msg.format(uid)
            return HttpResponse(err_msg)
    elif request.method == 'POST' :
        sql = "select uid, nick, lv, exp, gem, gold, stamina, char_cnt, skill_cnt, ss_id, state, play_time, DATE_FORMAT(last_dt, '%%Y%%m%%d') last_dt FROM zu_user_info WHERE uid = %s ORDER BY last_dt"
        curs.execute(sql, uid)
        rows = curs.fetchone()

        if rows != None:
            data = json.dumps(rows)
        else :
            sql = """
            INSERT INTO djangotest.zu_user_info (uid, nick, lv, `exp`, gem, gold, stamina, char_cnt, skill_cnt, ss_id, state, grade, play_time, last_dt)
            VALUES(%s, %s, 1, 0, 0, 0, 0, 0, 0, %s, 0, 0, 0, now());
            """
            curs.execute(sql, (uid, nick, ss_num))
            conn.commit()

            insert_cnt = curs.rowcount
            ins_msg = '''{}건 Insert 완료'''
            data = ins_msg.format(insert_cnt)
        conn.close()
        return HttpResponse(data)