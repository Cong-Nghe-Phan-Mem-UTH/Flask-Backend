from flask import Blueprint, jsonify

test_bp = Blueprint('test', __name__, url_prefix='/test')

@test_bp.route('/', methods=['GET'])
def test():
    return jsonify({'message': 'Hello from test route!'})

