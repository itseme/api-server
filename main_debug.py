from itseme.app import app
from itseme.tasks import celery, mail

if __name__ == '__main__':
    app.config.from_object("itseme.config.DebugConfig")
    celery.conf.update(app.config)
    mail.init_app(app)
    app.run()
