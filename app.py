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
        fields = ('id', 'name', '_links')

    _links = ma.Hyperlinks({
            'self': ma.URLFor('create_kid', id='<id>'),
            'self': ma.URLFor('get_kid', id='<id>'),
            'collection': ma.URLFor('list_kids')
        })


kid_schema = KidSchema()
kids_schema = KidSchema(many=True)


@app.route('/kids', methods=['GET'], strict_slashes=False)
def list_kids() :
    all_kids = KidModel.query.all()
    app.logger.debug('fetched %s kids', len(all_kids))
    return jsonify(kids_schema.dump(all_kids))


@app.route('/kids/', methods=['POST'])
def create_kid() :
    name = request.json.get('name', '')

    kid = KidModel(name=name)

    db.session.add(kid)
    db.session.commit()

    app.logger.debug('New kid %s', kid_schema.dump(kid))
    return kid_schema.jsonify(kid)


@app.route('/kids/<int:id>/', methods=["GET"], strict_slashes=False)
def get_kid(id):
    kid = KidModel.query.get(id)
    app.logger.debug('Get kid id=%s', kid_schema.dump(kid))
    return kid_schema.jsonify(kid)


@app.route('/kids/<int:kid_id>/', methods=["DELETE"], strict_slashes=False)
def delete_kid(kid_id):
    kid = KidModel.query.get(kid_id)
    
    db.session.delete(kid)
    db.session.commit()

    return kid_schema.jsonify(kid)


if __name__ == '__main__' :
    app.run(debug=True)
