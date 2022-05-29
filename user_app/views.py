# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt

import pymysql, json, random, string


def null(request) :
    return HttpResponse('Null Page..')


@csrf_exempt
def login(request) :
    conn = pymysql.connect(host="27.96.130.7", port=3306, user="root", password="!Qpp041096", db="djangotest", charset="utf8")
    curs = conn.cursor(pymysql.cursors.DictCursor)

    uid           = request.GET.get('uid')
    member_id     = request.GET.get('member_id')
    platform_type = request.GET.get('platform_type')
    platform_id   = request.GET.get('platform_id')
    push_id       = request.GET.get('push_id')

    login_info_sql = "select 'true' result, if(tutorial_yn = 'N', 'false', 'true') tutorial FROM zu_user_tmp WHERE uid = %s"
    curs.execute(login_info_sql, uid)
    rows = curs.fetchone()

    # DB에서 조회가 안되었을때 예외처리를(Catch try) 해야 함..
    # 현재 예외처리는 조회가 되었다 안되었다 뿐이라서.. 정확한 예외처리라 볼 수 없음.
    if rows :
        conn.close()
        data = json.dumps(rows)
    else :
        sql = """
        INSERT INTO djangotest.zu_user_tmp (uid, member_id, platform_type, platform_id, push_id, tutorial_yn, audit_dtm)
        VALUES(%s, %s, %s, %s, %s, 'N', now());
        """
        curs.execute(sql, (uid, member_id, platform_type, platform_id, push_id))
        conn.commit()
        conn.close()
        insert_cnt = curs.rowcount

        if insert_cnt == 1 :
            curs.execute(login_info_sql, uid)
            rows = curs.fetchone()
            data = json.dumps(rows)
        else :
            data = {
                "result" : 'false',
                "type" : 'err',
                "msg" : "계정등록에 실패하였습니다"
            }
            data = json.dumps(data, ensure_ascii=False)
            return HttpResponse(data, status=500)
    return HttpResponse(data)


@csrf_exempt
def info(request) :
    # Conn부분을 함수내에 입력하지 않을경우 세션연결 이슈가 있음..
    # 별도 모듈을 만들어서 옮겨서 사용해도 문제없을지 확인필요..
    conn = pymysql.connect(host="27.96.130.7", port=3306, user="root", password="!Qpp041096", db="djangotest", charset="utf8")
    curs = conn.cursor(pymysql.cursors.DictCursor)

    user_info_sql = "select uid, nick, lv, exp, gem, gold, stamina, char_cnt, skill_cnt, ss_id, uuid, state, play_time, DATE_FORMAT(last_dt, '%%Y%%m%%d') last_dt FROM zu_user_info WHERE uid = %s"

    uid = request.GET.get('uid')
    nick = request.GET.get('nick')
    ssid = request.GET.get('ssid')
    uuid = request.GET.get('uuid')

    if uid == '' or uid is None :
        data = {
            "result" : 'false',
            "type" : 'err',
            "msg" : "유저고유ID(UID)는 필수 입력값입니다"
        }
        data = json.dumps(data, ensure_ascii=False)
        return HttpResponse(data, status=400)

    if nick == '' or nick is None :
        # Get은 UID만 가지고도 조회가 가능하기때문에 Nick Parm에 대해 체크하지 않음.
        if request.method == 'POST' :
            data = {
                "result" : 'false',
                "type" : 'err',
                "msg" : "닉네임(NICK)은 필수 입력값입니다"
            }
            data = json.dumps(data, ensure_ascii=False)
            return HttpResponse(data, status=400)

    # 클라에서 기본적으로 신규유저, 기존유저를 체크해서..
    # 신규유저면 POST.., 기존유저면 GET으로 요청을 한다는 조건하에.. 아래의 로직을 생성.
    #if ssid == '' or ssid is None :
    #    if request.method == 'GET' :
    #        ssid = 100

    ss_num = "".join([random.choice(string.ascii_letters) for _ in range(15)])

    #ssid_rtn = {
    #    "ss_id" : ss_num
    #}

    if request.method == 'GET' :
        curs.execute(user_info_sql, uid)
        rows = curs.fetchone()
        select_cnt = curs.rowcount

        if select_cnt == 1 :
            #ss_id_chk = rows["ss_id"]
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
            #ssid_rtn = json.dumps(ssid_rtn)
            data = json.dumps(rows)
            #return HttpResponse((ssid_rtn, data))
            return HttpResponse(data)
        else :
            conn.close()
            data = {
                "result" : 'false',
                "type" : 'err',
                "msg" : "존재하지 않는 유저정보입니다."
            }
            data = json.dumps(data, ensure_ascii=False)
            return HttpResponse(data, status=400)

    elif request.method == 'POST' :
        curs.execute(user_info_sql, uid)
        rows = curs.fetchone()
        select_cnt = curs.rowcount

        if select_cnt == 1 :
            data = json.dumps(rows)
        else :
            # 변수와 문자 합치는 법.. 알아보기
            sql = """
            INSERT INTO djangotest.zu_user_info (uid, nick, lv, exp, gem, gold, stamina, char_cnt, skill_cnt, ss_id, uuid, state, grade, play_time, last_dt)
            VALUES(%s, %s, 1, 0, 100, 100, 100, 1, 1, %s, %s, 0, 0, 0, now());
            """
            curs.execute(sql, (uid, nick, ss_num, uuid))
            if curs.rowcount == 1 :
                conn.commit()
            else :
                data = {
                    "result" : 'false',
                    "type" : 'err',
                    "msg" : "계정등록에 실패하였습니다"
                }
                data = json.dumps(data, ensure_ascii=False)
                return HttpResponse(data, status=500)

            curs.execute(user_info_sql, uid)
            rows = curs.fetchone()
            data = json.dumps(rows)
        conn.close()
        return HttpResponse(data)


@csrf_exempt
def inven(request) :
    conn = pymysql.connect(host="27.96.130.7", port=3306, user="root", password="!Qpp041096", db="djangotest", charset="utf8")
    curs = conn.cursor()

    uid = request.GET.get('uid')

    cahr_info_sql = "select uid, char_uid, char_idx, type, grade, enchant_lv, DATE_FORMAT(get_dt, '%%Y%%m%%d') get_dt FROM zu_user_char_inven WHERE uid = %s"
    curs.execute(cahr_info_sql, uid)
    rows = curs.fetchall()
    select_cnt = curs.rowcount

    if rows :
        data = json.dumps(rows)
    else :
        # 원래는 NFD 오류로 뱉어야 하나..
        # 현재는 테스트상황이기에 데이터가 없을경우 임의로 Insert함..
        #data = {
        #    "result" : 'false',
        #    "type" : 'err',
        #    "msg" : "저장된 캐릭터 정보가 없습니다"
        #}
        sql = """
            INSERT INTO zu_user_char_inven (uid, char_uid, char_idx, type, grade, enchant_lv, get_dt, audit_dtm)
            VALUES(%s, 1, 1001, 'A', 'E', 0, DATE_FORMAT(now(), '%%Y%%m%%d'), now());
        """
        curs.execute(sql, uid)
        if curs.rowcount == 1 :
            conn.commit()

            curs.execute(cahr_info_sql, uid)
            rows = curs.fetchall()
            data = json.dumps(rows)
        else :
            conn.close()
            data = {
                "result" : 'false',
                "type" : 'err',
                "msg" : "계정등록에 실패하였습니다"
            }
            data = json.dumps(data, ensure_ascii=False)
            return HttpResponse(data, status=500)
    conn.close()
    return HttpResponse(data)