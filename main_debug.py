from itseme.app import app
from itseme.tasks import celery, mail


@app.after_request
def add_cross(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

app.config.from_object("itseme.config.DebugConfig")
celery.conf.update(app.config)
celery.app = app
mail.init_app(app)

if __name__ == '__main__':
    app.run()
