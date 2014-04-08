from itseme.app import app
from itseme.tasks import celery, mail

app.config.from_object("itseme.config.ProductionConfig")
celery.conf.update(app.config)
celery.app = app
mail.init_app(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
