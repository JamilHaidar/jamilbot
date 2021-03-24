from flask import Flask
from flask import render_template  
import jamilbot
from threading import Thread

Thread(target=jamilbot.run).start()

app = Flask(__name__)

@app.route('/index',methods=['GET','POST'])  
@app.route("/",methods=['GET','POST'])
def index():
    return render_template('index.html'),200