from flaskApp.models import * 
from flaskApp.settings import * 
from werkzeug.security import check_password_hash


def isRegistered(email):
    conn = mysql.connect()
    cursor = conn.cursor()
    query_string = "SELECT * FROM users_eg WHERE email = %s;"
    cursor.execute(query_string,email)
    result = cursor.fetchall()
    if len(result) == 1:
        return True
    else:
        return False
    
def check_username_exist(username):
    conn = mysql.connect()
    cursor = conn.cursor()
    query_string = "SELECT * FROM users_eg WHERE username = %s;"
    cursor.execute(query_string,username)
    result = cursor.fetchall()
    if len(result) == 1:
        return True
    else:
        return False

def get_userID(username):
    conn = mysql.connect()
    cursor = conn.cursor()
    query_string = "SELECT * FROM users_eg WHERE username = %s;"
    cursor.execute(query_string,username)
    result = cursor.fetchone()
    return result[0]

def get_user_data(username):
    conn = mysql.connect()
    cursor = conn.cursor()
    query_string = "SELECT * FROM users_eg WHERE username = %s;"
    cursor.execute(query_string,username)
    userData = cursor.fetchone()
    return userData

def checkPassword(user_id,password):
    conn = mysql.connect()
    cursor = conn.cursor()
    query_string = "SELECT * FROM users_eg WHERE id = %s;"
    cursor.execute(query_string,user_id)
    result = cursor.fetchone()
    login_password = result[3] 
    return check_password_hash(login_password,password)

def checkFavDuplicate(video_id,user_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    query_string = "SELECT * FROM favourite_eg WHERE video_id = %s AND user_id = %s;"
    cursor.execute(query_string,(video_id,user_id))
    result = cursor.fetchall()
    if len(result) > 0:
        return True
    else:
        return False




        
    