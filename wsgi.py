from app.main import app
  
if __name__ == "__main__":
        print('In wsgi')
        app.run()
        print('In wsgi: ran flask')
        import jamilbot
        print('In wsgi: imported jamilbot')