from __future__ import absolute_import
import os
import sys
import json

# insert the root dir into the system path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from transformer import registry
from transformer.util import APIError

from flask import Flask, jsonify, request


# Create our Flask App
app = Flask(__name__)

# Prepare the application transform registry
registry.make_registry()


@app.route("/")
def hello():
    """ Returns a list of transforms available to be used """
    data = request.args
    transforms = registry.get_all(category=data.get('category'))
    return jsonify(transforms=[v.to_dict() for v in transforms])


@app.route("/fields")
def fields():
    """ Returns a list of fields for a given transform """
    data = request.args
    if not data or 'transform' not in data:
        raise APIError('Missing transform', 400)

    transform = registry.lookup(data['transform'], category=data.get('category'))
    if not transform:
        raise APIError('Transform "{}" not found'.format(data['transform']), 404)

    inputs = data.get('inputs')
    fields = transform.all_fields(inputs=inputs)

    return jsonify(fields=fields)


@app.route("/transform", methods=["POST"])
def transform():
    """ Perform a transformation """
    try:
        data = json.loads(request.data)
    except:
        raise APIError('Missing or malformed request body', 400)

    if not data:
        raise APIError('Missing request body', 400)

    if not data.get('transform'):
        raise APIError('Missing transform', 400)

    if 'inputs' not in data:
        raise APIError('Missing input data', 400)

    transform = registry.lookup(data['transform'], category=data.get('category'))
    if not transform:
        raise APIError('Transform "{}" not found'.format(data['transform']), 404)

    inputs = data.pop('inputs')

    outputs = transform.transform_many(inputs, data)

    return jsonify(outputs=outputs)


@app.errorhandler(APIError)
def error(e):
    """ Handle our APIError exceptions """
    response = jsonify(e.to_dict())
    response.status_code = e.status_code
    return response


@app.errorhandler(Exception)
def exception(e):
    """ Handle generic exceptions """
    response = jsonify(message=str(e))
    response.status_code = 500
    return response


def serve_locally(app):
    """
    serve this flask application locally

    """
    port = int(os.environ.get('PORT', 5000))
    debug = True if os.environ.get('DEBUG', 'false') == 'true' else False
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    serve_locally(app)
