from flask import Flask
from flask import render_template,redirect
import os
app = Flask(__name__)

@app.route('/index',methods=['GET','POST'])  
@app.route("/",methods=['GET','POST'])
def index():
    return render_template('index.html'),200

@app.route('/embrace',methods=['GET'])
def embrace():
    return redirect("tel://1564")