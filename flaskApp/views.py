from flaskApp.settings import *
from flask import render_template

def landingPage():
    return render_template('landing.html')

def loginPage():
    return render_template('login.html')

def registerPage():
    return render_template('register.html')

def homePage():
    return render_template('home.html')

def chest_yt_page():
    return render_template('chest_yt.html')

def back_yt_page():
    return render_template('back_yt.html')

def arm_yt_page():
    return render_template('arm_yt.html')

def shoulder_yt_page():
    return render_template('shoulder_yt.html')

def leg_yt_page():
    return render_template('leg_yt.html')

def abs_yt_page():
    return render_template('abs_yt.html')

def favouritePage():
    return render_template('favourite.html')

def profilePage():
    return render_template('profile.html')

def myWorkoutPage():
    return render_template('my_workout.html')

def myChestPage():
    return render_template('mychest.html')

def myBackPage():
    return render_template('myback.html')

def myArmPage():
    return render_template('myarm.html')

def myAbsPage():
    return render_template('myabs.html')

def myLegPage():
    return render_template('myleg.html')

def myShoulderPage():
    return render_template('myshoulder.html')