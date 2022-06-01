# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt

import pymysql, json, random, string


def null(request) :
    return HttpResponse('Null Page..')


def inputparmchk(function_nm, member_id, parm1, parm2, parm3, parm4) :
    print("function_nm " + function_nm)
    print("member_id " +member_id)
    print("parm1 " +parm1)
    print("parm2 " +parm2)
    print("parm3 " +parm3)
    print("parm4 " +parm4)
    if member_id == '' or member_id is None :
        print("member_id if 인입..")
        data = {
            "result" : 'false',
            "type" : 'err',
            "msg" : "member_id 는 필수 입력값입니다"
        }
        data = json.dumps(data, ensure_ascii=False)
        return HttpResponse(data)

    if function_nm == "login" :
        if parm1 == '' or parm1 is None :
            print("platform_type if 인입..")
            data = {
                "result" : 'false',
                "type" : 'err',
                "msg" : "platform_type 는 필수 입력값입니다"
            }
            data = json.dumps(data, ensure_ascii=False)
            return HttpResponse(data)
        if parm2 == '' or parm2 is None :
            print("platform_id if 인입..")
            data = {
                "result" : 'false',
                "type" : 'err',
                "msg" : "platform_id 는 필수 입력값입니다"
            }
            data = json.dumps(data, ensure_ascii=False)
            return HttpResponse(data)
        if parm3 == '' or parm3 is None :
            print("push_id if 인입..")
            data = {
                "result" : 'false',
                "type" : 'err',
                "msg" : "push_id 는 필수 입력값입니다"
            }
            data = json.dumps(data, ensure_ascii=False)
            return HttpResponse(data)

    elif function_nm == "info" :
        if parm1 == '' or parm1 is None :
            print("ss_id if 인입..")
            data = {
                "result" : 'false',
                "type" : 'err',
                "msg" : "ss_id 는 필수 입력값입니다"
            }
            data = json.dumps(data, ensure_ascii=False)
            return HttpResponse(data)
        if parm2 == '' or parm2 is None :
            print("uuid if 인입..")
            data = {
                "result" : 'false',
                "type" : 'err',
                "msg" : "uuid 는 필수 입력값입니다"
            }
            data = json.dumps(data, ensure_ascii=False)
            return HttpResponse(data)


@csrf_exempt
def login(request) :
    if request.method == 'GET' :
        data = {
            "result" : 'false',
            "type" : 'err',
            "msg" : "잘못된 API호출(GET으로 요청이 이루어졌습니다)"
        }
        data = json.dumps(data, ensure_ascii=False)
        return HttpResponse(data)

    conn = pymysql.connect(host="27.96.130.7", port=3306, user="root", password="!Qpp041096", db="djangotest", charset="utf8")
    curs = conn.cursor(pymysql.cursors.DictCursor)

    member_id     = request.GET.get('member_id')
    platform_type = request.GET.get('platform_type')
    platform_id   = request.GET.get('platform_id')
    push_id       = request.GET.get('push_id')

    data = inputparmchk("login", member_id, platform_type, platform_id, push_id, '')
    if data is not None :
        return HttpResponse(data)

    login_info_sql = "select 'true' result, if(tutorial_yn = 'N', 'false', 'true') tutorial FROM zu_user_tmp WHERE member_id = %s and platform_id = %s and push_id = %s"
    curs.execute(login_info_sql, (member_id, platform_id, push_id))
    rows = curs.fetchone()

    if rows :
        conn.close()
        data = json.dumps(rows)
    else :
        sql = """
        INSERT INTO zu_user_tmp (member_id, platform_type, platform_id, push_id, tutorial_yn, audit_dtm)
        VALUES(%s, %s, %s, %s, 'N', now())
        """
        curs.execute(sql, (member_id, platform_type, platform_id, push_id))
        conn.commit()
        insert_cnt = curs.rowcount

        if insert_cnt == 1 :
            curs.execute(login_info_sql, (member_id, platform_id, push_id))
            rows = curs.fetchone()
            data = json.dumps(rows)
        else :
            data = {
                "result" : 'false',
                "type" : 'err',
                "msg" : "계정등록에 실패하였습니다"
            }
            data = json.dumps(data, ensure_ascii=False)
        conn.close()
    return HttpResponse(data)


@csrf_exempt
def info(request) :
    if request.method == 'GET' :
        data = {
            "result" : 'false',
            "type" : 'err',
            "msg" : "잘못된 API호출(GET으로 요청이 이루어졌습니다)"
        }
        data = json.dumps(data, ensure_ascii=False)
        return HttpResponse(data)

    # Conn부분을 함수내에 입력하지 않을경우 세션연결 이슈가 있음..
    # 별도 모듈을 만들어서 옮겨서 사용해도 문제없을지 확인필요..
    conn = pymysql.connect(host="27.96.130.7", port=3306, user="root", password="!Qpp041096", db="djangotest", charset="utf8")
    curs = conn.cursor(pymysql.cursors.DictCursor)

    member_id = request.GET.get('member_id')
    ssid = request.GET.get('ssid')
    uuid = request.GET.get('uuid')

    data = inputparmchk("info", member_id, ssid, uuid, '', '')
    if data is not None :
        return HttpResponse(data)

    user_info_sql = "select member_id, lv, exp, stage, gem, gold, stamina, char_cnt, skill_cnt, ss_id, uuid, state, grade, play_time, DATE_FORMAT(last_dt, '%%Y%%m%%d') last_dt FROM zu_user_info WHERE member_id = %s"

    #if ssid == '' or ssid is None :
    #    if request.method == 'GET' :
    #        ssid = 100

    ss_num = "".join([random.choice(string.ascii_letters) for _ in range(15)])

    #ssid_rtn = {
    #    "ss_id" : ss_num
    #}

    curs.execute(user_info_sql, member_id)
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

        ss_id_update_sql = "update zu_user_info set ss_id = %s where member_id = %s"
        curs.execute(ss_id_update_sql, (ss_num, member_id))
        conn.commit()
        data = json.dumps(rows)
    else :
        insert_sql = """
        INSERT INTO zu_user_info (member_id, lv, exp, stage, gem, gold, stamina, char_cnt, skill_cnt, ss_id, uuid, state, grade, play_time, last_dt)
        VALUES(%s, 1, 0, 0, 100, 100, 100, 1, 1, %s, %s, 0, 0, 0, now())
        """
        curs.execute(insert_sql, (member_id, ss_num, uuid))
        if curs.rowcount == 1 :
            conn.commit()
            curs.execute(user_info_sql, member_id)
            rows = curs.fetchone()
            data = json.dumps(rows)
        else :
            data = {
                "result" : 'false',
                "type" : 'err',
                "msg" : "계정등록에 실패하였습니다"
            }
            data = json.dumps(data, ensure_ascii=False)
    conn.close()
    return HttpResponse(data)


@csrf_exempt
def inven(request) :
    if request.method == 'GET' :
        data = {
            "result" : 'false',
            "type" : 'err',
            "msg" : "잘못된 API호출(GET으로 요청이 이루어졌습니다)"
        }
        data = json.dumps(data, ensure_ascii=False)
        return HttpResponse(data)

    conn = pymysql.connect(host="27.96.130.7", port=3306, user="root", password="!Qpp041096", db="djangotest", charset="utf8")
    curs = conn.cursor()

    member_id = request.GET.get('member_id')

    data = inputparmchk("inven", member_id, '', '', '', '')
    if data is not None :
        return HttpResponse(data)

    cahr_info_sql = "select member_id, char_uid, char_idx, type, grade, enchant_lv, DATE_FORMAT(get_dt, '%%Y%%m%%d') get_dt FROM zu_user_char_inven WHERE member_id = %s"
    curs.execute(cahr_info_sql, member_id)
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
        insert_sql = """
        INSERT INTO zu_user_char_inven (member_id, char_uid, char_idx, type, grade, enchant_lv, get_dt, audit_dtm)
        VALUES(%s, 1, 1001, 'A', 'E', 0, DATE_FORMAT(now(), '%%Y%%m%%d'), now());
        """
        curs.execute(insert_sql, member_id)
        if curs.rowcount == 1 :
            conn.commit()

            curs.execute(cahr_info_sql, member_id)
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
    conn.close()
    return HttpResponse(data)