from flask import Flask, jsonify, request
from modules.youtube_db import PostSearch
from raven.contrib.flask import Sentry
app = Flask(__name__)

sentry = Sentry(app)


# @app.route('/api/v1/search/<string:q>')
@app.route('/api/v1/search')
def search():
    query = request.args.get('q')
    youtube_api = PostSearch()
    result = youtube_api.db_check(query)
    return jsonify(result)


if __name__ == '__main__':
    app.run(port=5017)
