from wsgiref import simple_server
from flask import Flask, request, render_template
from flask import  Response
from flask_cors import CORS, cross_origin
from apps.training.train_model import TrainModel

from apps.core.config import Config

app = Flask(__name__)
CORS(app)

@app.route('/training', methods=['POST'])
@cross_origin()
def training_route_client():
    """
    Method that handles the training process

    Args:
        None
    Returns:
        None
    """

    try:
        config = Config()
        run_id = config.get_run_id() # Get the run id of the training
        data_path = config.training_data_path # Declare the data path
        # Initialize the train model object
        trainModel = TrainModel(run_id, data_path)
        # Start the training process
        trainModel.training_model()
        return Response(f'Training process with run_id: {run_id} was successful')

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