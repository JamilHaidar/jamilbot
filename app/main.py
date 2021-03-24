from flask import Flask
from flask import render_template  
import os
app = Flask(__name__)

@app.route('/index',methods=['GET','POST'])  
@app.route("/",methods=['GET','POST'])
def index():
    return render_template('index.html'),200
