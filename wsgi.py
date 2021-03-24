from app.main import app
from threading import Thread
if __name__ == "__main__":
        print('In wsgi')
        flasktask = Thread(target=app.run).start()
        print('In wsgi: ran flask')
        import jamilbot
        print('In wsgi: Import done. running..')
        jamilbot.run()
        print('Done running')
        flasktask.join()
