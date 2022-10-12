from wsgiref import simple_server
from flask import Flask, request, render_template
from flask import  Response
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

@app.route('/training', methods=['POST'])
@cross_origin()
def training_route_client():
    try:
        return Response('Training successful')
    except ValueError:
        return Response(f'Error occured! {ValueError}')
    except KeyError:
        return Response(f'Error occured! {KeyError}')
    except Exception as e:
        return Response(f'Error occured! {e}')

if __name__ == '__main__':
    host = "localhost"
    port = 5000
    httpd = simple_server.make_server(host, port, app)
    httpd.serve_forever()