import datetime
import mongoengine
import sys
sys.path.append('..')
sys.path.append('../../libs')

from config import Config
from flask import Flask, render_template
import mongoengine

## Initializing the app
app = Flask(__name__)
app.debug = True
config = Config()


@app.route('/')
def index():
    return render_template('index.html', user=user)

if __name__ == "__main__":
    #if len(sys.argv) > 1: 
    #    config = GlobalConfig.from_json(sys.argv[1])
    db = mongoengine.connect(config.health_monitor.mongo_db)

    app.run(host="0.0.0.0", port=config.web_server.port, debug=True)