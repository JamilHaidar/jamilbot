from app.main import app
print('Starting wsgi')

if __name__ == "__main__":
        print('In wsgi')
        print('In wsgi: Import done. running..')
        app.run()
        print('In wsgi: ran flask')
        print('Done running')