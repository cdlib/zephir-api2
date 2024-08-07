import markdown
from flask import Blueprint, current_app, jsonify, make_response, redirect, request, url_for
from markupsafe import Markup
from sqlalchemy.orm.exc import NoResultFound

from .models import ZephirFiledata


blueprint = Blueprint('blueprint', __name__)


@blueprint.before_request
def handle_content_negotiation():
    """
    Extensions are prioritized over Accept headers. If no extension is provided, the Accept header is used.
    """
    current_app.logger.debug(f"Path: {request.path}")
    current_app.logger.debug(f"Accept: {request.accept_mimetypes}")
    if request.path.endswith('.json'):
        request.desired_content_type = 'application/json'
    elif request.path.endswith('.xml'):
        request.desired_content_type = 'text/xml'
    elif 'application/json' in request.accept_mimetypes.values():
        request.desired_content_type = 'application/json'
    elif 'text/xml' in request.accept_mimetypes.values():
        request.desired_content_type = 'text/xml'
    else:
        request.desired_content_type = 'text/xml'


@blueprint.route('/')
def index():
    return redirect(url_for('blueprint.documentation'), code=303)


@blueprint.route('/documentation')
def documentation():
    # Read the Markdown file
    with open('API.md', 'r') as file:
        content = file.read()

    # Convert Markdown to HTML
    html_content = markdown.markdown(content.replace('http://localhost/', request.url_root))

    # Return HTML content. The Markup class prevents Flask from escaping HTML content.
    return Markup(html_content)


@blueprint.route('/ping')
@blueprint.route('/ping.xml')
@blueprint.route('/ping.json')
def ping():
    if not ZephirFiledata.query.first():
        raise Exception('Database check failed')
    else:
        return render_basic_response(200, 'Success')


@blueprint.route('/item', defaults={'htid': None})
@blueprint.route('/item/<path:htid>')
@blueprint.route('/item/<path:htid>.xml')
@blueprint.route('/item/<path:htid>.json')
def item(htid):
    current_app.logger.debug(f"RAW HTID: {htid}")
    htid = validate_htid(htid)
    current_app.logger.debug(f"HTID: {htid}")
    item = ZephirFiledata.query.filter_by(htid=htid).first()
    if item is None:
        raise NoResultFound(f"No results found for HTID: {htid}")
    
    current_app.logger.debug(f'desired content type: {request.desired_content_type}')

    if request.desired_content_type == 'application/json':
        content = make_response(item.metadata_json)
        content.headers['Content-Type'] = 'application/json'
    else:
        content = make_response(item.metadata_xml)
        content.headers['Content-Type'] = 'text/xml'
    return content


@blueprint.errorhandler(Exception)
def handle_exception(error):
    print(error)
    if isinstance(error, NoResultFound):
        return render_basic_response(404, str(error))
    elif isinstance(error, UnacceptableParameterException):
        return render_basic_response(422, str(error))
    else:
        return render_basic_response(500, 'Failure')
    

@blueprint.errorhandler(404)
def handle_404(error):
    return render_basic_response(400, 'Bad Request')


# Utilities
class UnacceptableParameterException(Exception):
    def __init__(self, msg='Unacceptable parameters', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


def render_basic_response(status_code, message):
    if request.desired_content_type == 'application/json':
        response = jsonify(status=status_code, message=message)
    else:
        response = make_response(f"<response><status>{status_code}</status><message>{message}</message></response>")
        response.headers['Content-Type'] = 'text/xml'
    return response, status_code


def validate_htid(htid):
    if 3 <= len(htid) <= 40:
        return htid
    raise UnacceptableParameterException()