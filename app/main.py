from flask import Flask
  
app = Flask(__name__)
  
@app.route("/",methods=['GET','POST'])
def home_view():
        return "<h1>Nothing to see here</h1>"