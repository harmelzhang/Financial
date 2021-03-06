import time

from flask import Flask, request, jsonify
from financial.category import category
from financial.stock import stock
from utils import sha1

app = Flask(__name__)
app.config.from_object('config')

app.register_blueprint(category)
app.register_blueprint(stock)


@app.before_request
def check_signature():
    if app.config['DEBUG']:
        return None

    # 跳过检查权限的URL
    skip_check_auth_urls = [
        '/favicon.ico'
    ]
    for url in skip_check_auth_urls:
        if request.path.startswith(url):
            return None

    secret = app.config['SECRET']
    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')

    no_auth_response = jsonify({
        'code': app.config['ERROR_CODE_NO_AUTH'],
        'message': '无权访问该接口'
    })

    if nonce is None or nonce == '' or timestamp is None or timestamp == '' or signature is None or signature == '':
        return no_auth_response

    now_timestamp = int(time.time())
    if not timestamp.isdigit() or abs(int(timestamp) - now_timestamp) > 30:
        return no_auth_response

    args = [f'secret={secret}']
    for key, value in request.args.items():
        if key != 'signature':
            args.append(f'{key}={value}')
    args.sort()

    if sha1('&'.join(args)) != signature:
        return no_auth_response


@app.errorhandler(500)
def handle_error(err):
    return jsonify({
        'code': app.config['ERROR_CODE_ERROR'],
        'message': f'{err.original_exception}'
    })
