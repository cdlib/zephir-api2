import logging
import re
from flask import Flask, request, jsonify, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
import markdown
from markupsafe import Markup
import yaml
import os

app = Flask(__name__)

# Set up basic configuration for logging
logging.basicConfig(level=logging.DEBUG)
# Log everything to stdout in debug mode
app.logger.setLevel(logging.DEBUG)
app.logger.debug(f"starting logger with level {app.logger.level}")

# Environment and Database Setup
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['APP_ROOT'] = os.path.abspath(os.path.dirname(__file__))

# Load database configuration
# db_config_path = os.path.join(app.config['APP_ROOT'], 'config', 'database.yml')
# with open(db_config_path, 'r') as file:
#     db_config = yaml.safe_load(file)['development']

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
DATABASE = os.getenv('DATABASE')

# Construct the database URI
db_uri = f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}?charset=utf8mb4"
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

db = SQLAlchemy(app)

# ORM for Database Interaction
class ZephirFiledata(db.Model):
    __tablename__ = 'zephir_filedata'
    htid = db.Column('id',db.Integer, primary_key=True)
    metadata_xml = db.Column('metadata',db.Text)
    metadata_json = db.Column(db.Text)

# Constants
re.compile(r'^([a-zA-Z0-9_]{3,40})(?:\.json|\.xml)?$')

@app.before_request
def handle_content_negotiation():
    app.logger.debug(f"Path: {request.path}")
    if request.path.endswith('.json'):
        request.desired_content_type = 'application/json'
    else: 
        request.desired_content_type = 'text/xml'

@app.route('/')
def index():
    return redirect(url_for('documentation'), code=303)

@app.route('/documentation')
def documentation():
    # Read the Markdown file
    with open('API.md', 'r') as file:
        content = file.read()

    # Convert Markdown to HTML
    html_content = markdown.markdown(sub_url(content))

    # Return HTML content. The Markup class prevents Flask from escaping HTML content.
    return Markup(html_content)

@app.route('/ping')
@app.route('/ping.xml')
@app.route('/ping.json')
def ping():
    if not ZephirFiledata.query.first():
        raise Exception('Database check failed')
    else:
        return render_basic_response(200, 'Success')

@app.route('/item', defaults={'htid': None})
@app.route('/item/<htid>')
@app.route('/item/<htid>.xml')
@app.route('/item/<htid>.json')
def item(htid):
    htid = validate_htid(htid)
    app.logger.debug(f"HTID: {htid}")
    item = ZephirFiledata.query.filter_by(htid=htid).first()
    if item is None:
        raise Exception('Not Found')
    
    # Determine the best match based on client's Accept header
    supported_types = ['application/json', 'text/xml']
    best = request.accept_mimetypes.best_match(supported_types)

    app.logger.debug(f"Request: {best}")
    if request.desired_content_type == 'application/json':
        content = make_response(item.metadata_json)
        content.headers['Content-Type'] = 'application/json'
    else:
        content = make_response(item.metadata_xml)
        content.headers['Content-Type'] = 'text/xml'
    return content


# @app.errorhandler(Exception)
# def handle_exception(error):
#     print(error)
#     if isinstance(error, KeyError):
#         return render_basic_response(404, 'Not Found')
#     elif isinstance(error, ValueError):
#         return render_basic_response(422, 'Unacceptable parameters')
#     else:
#         return render_basic_response(500, 'Failure')

# @app.errorhandler(404)
# def handle_404(error):
#     return render_basic_response(400, 'Bad Request')

def sub_url(text):
    return text.replace('http://localhost/', request.url_root)

def render_basic_response(status_code, message):
    if request.desired_content_type == 'application/json':
        response = jsonify(status=status_code, message=message)
    else:
        response = make_response(f"<response><status>{status_code}</status><message>{message}</message></response>")
        response.headers['Content-Type'] = 'text/xml'
    return response, status_code

HTID_REGEX = re.compile(r'^([\w.]{3,40})$')
def validate_htid(htid):
    match = re.match(HTID_REGEX, htid)
    if not match:
        raise Exception('Unacceptable parameters')
    return match.group(1)
    
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
