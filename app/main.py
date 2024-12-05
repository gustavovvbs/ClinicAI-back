import logging
from flask import Flask, Blueprint, request, jsonify 
from app.db.mongo_client import init_db
from app.api.endpoints.auth import auth_bp
from app.api.endpoints.email import email_bp
from app.api.endpoints.user import user_bp
from app.api.endpoints.search import search_bp
from app.api.endpoints.study import study_bp
from app.api.endpoints.excel import excel_bp
from app.api.endpoints.chatbot import chatbot_bp
from app.api.endpoints.pdf import pdf_bp
from app.api.endpoints.scheduler import scheduler_bp
from app.api.endpoints.data_analysis import data_analysis_bp


from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    init_db(app)
    app.register_blueprint(auth_bp, url_prefix = '/auth')
    app.register_blueprint(user_bp, url_prefix = '/user')
    app.register_blueprint(search_bp, url_prefix = '/search')
    app.register_blueprint(email_bp, url_prefix='/email')
    app.register_blueprint(study_bp, url_prefix='/study')
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    app.register_blueprint(pdf_bp, url_prefix='/pdf')
    app.register_blueprint(excel_bp, url_prefix='/excel')
    app.register_blueprint(data_analysis_bp, url_prefix='/data')
    app.register_blueprint(scheduler_bp)


    logging.basicConfig(level=logging.ERROR)
    return app

app = create_app()
    
@app.route('/')
def index():
    return jsonify({'message': 'Hello World'})

