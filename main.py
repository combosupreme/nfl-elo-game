import flask
from fte_predictor import eval as fte_predictor

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return "<h1>NFL ELO API</h!>"

@app.route('/api/v1/get_week_prediction', methods=['GET'])
def get_prediction():
    eval = fte_predictor.call_predictor(get_updates=False, k_value=None, hfa_value=None, revert_value=None, condensed_version=False, dont_show_this_weeks_games=False)
    result = eval['upcoming_games']
    return flask.jsonify(result)
    
    
if __name__ == '__main__':
    app.run()