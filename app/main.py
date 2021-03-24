from flask import Flask
from flask import render_template  
app = Flask(__name__)

@app.route('/index',methods=['GET','POST'])  
@app.route("/",methods=['GET','POST'])
def index():
    user = {'username': 'Miguel'}
    return render_template('index.html'),200