from flask import Flask
import os
CAAKA_SECRET=os.environ.get("CAAKA_SECRET")

def create_app(test_config=None):
    # create and configure the app
 
    from . import settings
    if settings.CAAKA_LOCAL:
        #for local development
        class MyFlask(Flask):
            def get_send_file_max_age(self, name):
                lower=name.lower()
                if lower.endswith('.js') or lower.endswith('.html') :
                    return 3
                return Flask.get_send_file_max_age(self, name)
        app = MyFlask('caakr', instance_relative_config=True)
        app.static_folder=settings.LOCAL_STATIC_FOLDER
        app.static_url_path='/static'
    else:
        app = Flask('caakr', instance_relative_config=True)
     
    app.config.from_mapping(
        SECRET_KEY=CAAKA_SECRET)

    #if test_config is None:
        # load the instance config, if it exists, when not testing
        #app.config.from_pyfile('config.py', silent=True)
    #else:
        # load the test config if passed in
        #app.config.from_mapping(test_config)

    # ensure the instance folder exists
    #try:
        #os.makedirs(app.instance_path)
    #except OSError:
        #pass

    from . import auth,jobupdate,home

    app.register_blueprint(auth.auth)
    app.register_blueprint(jobupdate.bp)
    app.register_blueprint(home.bp)
    return app
