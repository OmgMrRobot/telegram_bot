import pymysql
import pass_key

host = pass_key.host
root = pass_key.root
pasw = pass_key.pasw

def reset(user_id):
    con = pymysql.connect(host, root, pasw, 'restarans')
    try:
        with con.cursor() as cursor:
            cursor.execute("DELETE FROM restarans.tb_users WHERE user_chat = (%s)", (user_id))
            con.commit()
    finally:
        con.close()


def list(user_id):
    con = pymysql.connect(host, root, pasw, 'restarans')
    try:
        with con.cursor() as cursor:

            cursor.execute( "SELECT * FROM tb_users WHERE user_chat = (%s) ORDER BY user_id DESC LIMIT 10", (user_id))
            result = cursor.fetchall()
    finally:
        con.close()
    return result

def add_notice(user_id, dict):

    con = pymysql.connect(host, root, pasw, 'restarans')
    try:
        with con.cursor() as cursor:
            cursor.execute(("""INSERT IGNORE INTO
              tb_users (user_chat, restaran_name, pic, loc_lan, loc_lon)
              VALUES (%s,%s,%s,%s,%s);"""),
                           (user_id, dict["name"], dict['picture'], dict['res_location'][0], dict['res_location'][1]))
        con.commit()
    finally:
        con.close()


