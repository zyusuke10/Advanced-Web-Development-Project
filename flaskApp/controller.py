from flaskApp.settings import *
from flask import request,jsonify,make_response,redirect,session,url_for
from flaskApp.views import loginPage,registerPage,landingPage,homePage,chest_yt_page,back_yt_page,arm_yt_page,shoulder_yt_page,leg_yt_page,abs_yt_page,favouritePage,profilePage,myWorkoutPage,myChestPage,myBackPage,myAbsPage,myArmPage,myLegPage,myShoulderPage
from flaskApp.models import *
from werkzeug.security import generate_password_hash
from datetime import datetime,timedelta
from flaskApp.tools import isRegistered,checkPassword,check_username_exist,get_userID,get_user_data,checkFavDuplicate
import jwt
import uuid
from functools import wraps

def token_required(func):
    @wraps(func)
    def decorated(*args,**kwargs):
        token=None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        if not token:
            print("Missing token")
            return redirect(url_for('login'),code=401)
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            print("token expired")
            return redirect(url_for('login'),code=401)
        except jwt.InvalidTokenError:
            print('Invalid token')
            return redirect(url_for('login'),code=401)
        return func(*args,**kwargs)
    return decorated

#//////////Business Logics/////////////////////
@app.route('/auth/login',methods=['GET','POST'])
def loginUser():
    if request.method == 'POST':
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return jsonify({'message': 'Missing required fields'}), 400
        if check_username_exist(auth.username) and checkPassword(get_userID(auth.username),auth.password):
            session['username'] = auth.username
            session_id = str(uuid.uuid4())
            response = make_response(jsonify({'message': 'Login successful'}),200)
            response.set_cookie('session_id', session_id, httponly=True)
            return response
        else:
             return jsonify({'message': 'Invalid username or password'}),400
    return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic auth="Login required"'}), 401


@app.route('/auth/register',methods=['GET','POST'])
def registerUser():
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        email = data['email']
        password = data['password']
        confirm_password = data['confirmPassword']

        if not data or not username or not email or not password or not confirm_password:
            return jsonify({'message' : 'Missing required fields'}),400
        
        if password == confirm_password:
            password = generate_password_hash( data['password'],method="sha256")
            if isRegistered(email):
                return jsonify({'message':'Email already exists'}),409
            else:
                if not check_username_exist(username):
                    query_string = "INSERT INTO users_eg(username,email,password)VALUES(%s,%s,%s);"
                    cursor.execute(query_string, (username,email,password))
                    conn.commit()
                    return make_response(jsonify({'message': 'User created'}),201)
                else:
                    return jsonify({'message':'Username already exists'}),409
        else:
            return jsonify({'message':'Check confirm password again'}),400
    conn.close()

@app.route("/updateUsername",methods=['GET','POST'])
@token_required
def updateUsername():
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        user_id = data['user_id']
        print(user_id)
        if not data or not username:
            return jsonify({'message' : 'Missing required fields'}),400
        if not check_username_exist(username):
            query_string = "UPDATE users_eg SET username = %s WHERE id = %s;"
            cursor.execute(query_string, (username,user_id))
            conn.commit()
            session['username'] = username
            return make_response(jsonify({'message': 'Username edited'}),200)
        else:
            return jsonify({'message':'Username already exists'}),409

@app.route("/updateEmail",methods=['GET','POST'])
@token_required
def updateEmail():
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        user_id = data['user_id']
        print(user_id)
        if not data or not email:
            return jsonify({'message' : 'Missing required fields'}),400
        if not isRegistered(email):
            query_string = "UPDATE users_eg SET email = %s WHERE id = %s;"
            cursor.execute(query_string, (email,user_id))
            conn.commit()
            return make_response(jsonify({'message': 'Email edited'}),200)
        else:
            return jsonify({'message':'Email already exists'}),409


@app.route('/logout')
def logout():
    session.clear()
    response = make_response(jsonify({'message': 'Logout successful'}),200)
    response.delete_cookie('session_id')
    return response

@app.route('/getFavourite', methods=['GET','POST'])
@token_required
def getFavourite():
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == "GET":
        if "username" in session:
            user_id = get_userID(session['username'])
        else:
            return redirect(url_for('login'),code=401)
        query_string = "SELECT * FROM favourite_eg WHERE user_id = %s"
        cursor.execute(query_string,(user_id))
        result = cursor.fetchall()
        return jsonify(result),200
    conn.close()

@app.route('/addFavourite', methods=['GET','POST'])
@token_required
def addFavourite():
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == "POST":
        data = request.get_json()
        video_id = data['video_id']
        if data and video_id is not None:
            if "username" in session:
                user_id = get_userID(session['username'])
            else:
                return redirect(url_for('login'),code=401)
            if checkFavDuplicate(video_id,user_id):
                return make_response(jsonify({'message': "Item already added to your favourite list"}),409)
            else:
                query_string = "INSERT INTO favourite_eg(user_id,video_id)VALUES(%s,%s);"
                cursor.execute(query_string, (user_id,video_id))
                conn.commit()
                return make_response(jsonify({'message': 'Added to favourite'}),201)
        else:
             return make_response(jsonify({'message': 'Video not found'}),404)
    conn.close()

@app.route('/deleteFavourite', methods=['GET','POST'])
@token_required
def deleteFavourite():
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == "POST":
        data = request.get_json()
        video_id = data['video_id']
        if data and video_id is not None:
            if "username" in session:
                user_id = get_userID(session['username'])
            else:
                return redirect(url_for('login'),code=401)
            query_string = "DELETE FROM favourite_eg WHERE user_id = %s and video_id = %s;"
            cursor.execute(query_string, (user_id,video_id))
            conn.commit()
            return make_response(jsonify({'message': 'Deleted from favourites'}),200)
        else:
            return make_response(jsonify({'message': 'Video not found'}),404)
    cursor.close()
    conn.close()

@app.route('/saveMyWorkout', methods=["POST"])
@token_required
def save_my_workout():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        if request.method == "POST":
            data = request.get_json()
            exercise_name = data['exercise_name']
            sets = data['sets']
            reps = data['reps']
            kg = data['kg']
            workout_type = data['type']

            if not data or not exercise_name or not sets or not reps or not kg:
                return jsonify({'error': 'Missing required fields'}), 400

            if "username" not in session:
                return jsonify({'error': 'Not logged in'}), 401

            user_id = get_userID(session['username'])
            query_string = "INSERT INTO my{}Workout_eg (exercise_name, sets, reps, kg, user_id) VALUES(%s,%s,%s,%s,%s)".format(workout_type)
            cursor.execute(query_string, (exercise_name, sets, reps, kg, user_id))
            conn.commit()

            return jsonify({'message': 'Workout created'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()
    
    return jsonify({'error': 'Invalid request'}), 400

@app.route('/getMyWorkout', methods=["POST"])
@token_required
def get_my_workout():
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == "POST":
        data = request.get_json()
        workout_type = data['type']
        if "username" not in session:
            return redirect(url_for('login'),code=401)
        user_id = get_userID(session['username'])
        query_string = "SELECT * FROM my{}Workout_eg WHERE user_id = %s".format(workout_type)
        cursor.execute(query_string,(user_id))
        result = cursor.fetchall()
        return jsonify(result),200
    conn.close()

@app.route('/getSpecificWorkout', methods=["POST"])
@token_required
def getSpecificWorkout():
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == "POST":
        data = request.get_json()
        workout_type = data['type']
        workout_id = data['workout_id']
        if "username" not in session:
            return redirect(url_for('login'),code=401)
        user_id = get_userID(session['username'])
        query_string = "SELECT * FROM my{}Workout_eg WHERE user_id = %s AND id=%s".format(workout_type)
        cursor.execute(query_string,(user_id,workout_id))
        result = cursor.fetchall()
        return jsonify(result),200
    conn.close()

@app.route('/deleteMyWorkout', methods=['GET','POST'])
@token_required
def deleteMyWorkout():
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == "POST":
        data = request.get_json()
        workout_id = data['workout_id']
        workout_type = data['type']
        if data and workout_id is not None:
            if "username" in session:
                user_id = get_userID(session['username'])
            else:
                return redirect(url_for('login'),code=401)
            query_string = "DELETE FROM my{}Workout_eg WHERE user_id = %s and id=%s".format(workout_type)
            cursor.execute(query_string, (user_id,workout_id))
            conn.commit()
            return make_response(jsonify({'message': 'Deleted from favourites'}),200)
        else:
            return make_response(jsonify({'message': 'Video not found'}),404)
    cursor.close()
    conn.close()

@app.route('/editMyWorkout', methods=['GET','POST'])
@token_required
def editMyWorkout():
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == "POST":
        data = request.get_json()
        workout_id = data['workout_id']
        workout_type = data['type']
        workout_name = data['workout_name']
        workout_reps = data['workout_reps']
        workout_sets = data['workout_sets']
        workout_kg = data['workout_kg']
        if data and workout_id and workout_type and workout_name and workout_reps and workout_kg and workout_sets and workout_kg:
            if "username" in session:
                user_id = get_userID(session['username'])
            else:
                return redirect(url_for('login'),code=401)
            query_string = "UPDATE my{}Workout_eg SET exercise_name = %s, sets = %s, reps = %s, kg = %s WHERE user_id = %s AND id=%s".format(workout_type)
            cursor.execute(query_string, (workout_name,workout_sets,workout_reps,workout_kg, user_id,workout_id))
            conn.commit()
            return make_response(jsonify({'message': 'Edited successfully'}),200)
        else:
            return jsonify({'error': 'Missing required fields'}), 400
    cursor.close()
    conn.close()
                
       
#////////////Functions//////////////////

@app.route('/auth/getToken',methods=['GET','POST'])
def getToken():
    if request.method == 'POST':
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return jsonify({'message': 'Missing required fields'}), 400
        if check_username_exist(auth.username) and checkPassword(get_userID(auth.username),auth.password):
            token = jwt.encode({
            'user':auth.username,
            'exp': datetime.utcnow() + timedelta(minutes=30)},app.config['SECRET_KEY'],algorithm='HS256')
            return jsonify({'token' : token}),200
        else:
            return jsonify({'message': 'Password is incorrect'}),400
    return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic auth="Login required"'}), 401

@app.route('/getUser',methods = ['GET'])
def getUser():
    if 'username' in session:
        userData = get_user_data(session['username'])
        return jsonify({'data': userData}),200
    else: 
        return jsonify({"message":"Authentication required"}),401
    
@app.route('/get_API_KEY',methods = ['GET'])
def get_API_KEY():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return jsonify({"API_KEY" : YOUTUBE_API_KEY}),200

@app.route('/redirectPage', methods=['POST'])
def redirectPage():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    new_url = request.json['new_url']
    return jsonify({'new_url': new_url}),200
    
#////////Pages/////////////////////////

@app.route("/")
def index():
    session_id = request.cookies.get('session_id')
    if 'username' in session or session_id:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('landing'))

@app.route('/register/')
def register():
    return registerPage()

@app.route('/login/')
def login():
    return loginPage()

@app.route('/landing/')
def landing():
    return landingPage()

@app.route('/home')
def home():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return homePage()

@app.route('/chest_yt')
def chest_yt():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return chest_yt_page()

@app.route('/back_yt')
def back_yt():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return back_yt_page()

@app.route('/arm_yt')
def arm_yt():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return arm_yt_page()

@app.route('/shoulder_yt')
def shoulder_yt():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return shoulder_yt_page()

@app.route('/leg_yt')
def leg_yt():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return leg_yt_page()

@app.route('/abs_yt')
def abs_yt():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return abs_yt_page()

@app.route('/favourite')
def favourite():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return favouritePage()

@app.route('/profile')
def profile():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return profilePage()

@app.route('/myworkout')
def myWorkout():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return myWorkoutPage()

@app.route('/mychest')
def myChest():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return myChestPage()

@app.route('/myback')
def myBack():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return myBackPage()

@app.route('/myarm')
def myArm():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return myArmPage()

@app.route('/myabs')
def myAbs():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return myAbsPage()

@app.route('/myleg')
def myLeg():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return myLegPage()

@app.route('/myshoulder')
def myShoulder():
    session_id = request.cookies.get('session_id')
    if session_id is None or "username" not in session:
        return redirect(url_for('login'),code=401)
    return myShoulderPage()



