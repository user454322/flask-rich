import os
from flask import Flask
from flask.globals import request
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ \
                os.path.join(basedir, 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class KidModel(db.Model) :
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name) :
        self.name = name

class KidSchema(ma.SQLAlchemyAutoSchema) :
    class Meta :
        model = KidModel
        load_instance = True

kid_schema = KidSchema()
kids_schema = KidSchema(many=True)


@app.route('/kids', methods=['GET'], strict_slashes=False)
def list_kids() :
    all_notes = KidModel.query.all()
    app.logger.debug('fetched %s kids', len(all_notes))
    return jsonify(kids_schema.dump(all_notes))


@app.route('/kids/', methods=['POST'])
def create_kid() :
    name = request.json.get('name', '')
    content = request.json.get('content', '')

    kid = KidModel(name=name, content=content)

    db.session.add(kid)
    db.session.commit()

    return kid_schema.jsonify(kid)


@app.route('/kids/<int:kid_id>/', methods=["GET"])
def get_kid(kid_id):
    kid = KidModel.query.get(kid_id)
    return kid_schema.jsonify(kid)


@app.route('/kid/<int:note_id>/', methods=["DELETE"])
def delete_kid(note_id):
    note = KidModel.query.get(note_id)
    
    db.session.delete(note)
    db.session.commit()

    return kid_schema.jsonify(note)


if __name__ == '__main__' :
    app.run(debug=True)
