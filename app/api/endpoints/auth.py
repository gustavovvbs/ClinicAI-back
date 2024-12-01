from flask import Blueprint, request, jsonify, current_app
from app.services.auth import AuthService
from app.schemas.auth import UserCreateSchema, UserLoginSchema
from app.core.validation_middleware import validate_json
from pydantic import ValidationError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@validate_json(UserCreateSchema)
def register_user(data: UserCreateSchema):
    try:
        current_app.logger.info('Register endpoint called')
        auth_service = AuthService()
        auth_service.register(user_data.model_dump())
        return jsonify({'message': 'user created successfully'}), 201

    except ValidationError as e:
        current_app.logger.error(f'Validation error: {str(e)}')
        return jsonify({'error': 'validation error', 'details': str(e)}), 400

    except Exception as e:
        current_app.logger.error(f'Internal server error: {e}')
        return jsonify({'error': f'internal server error {e}'}), 500

@auth_bp.route('/login', methods=['POST'])
@validate_json(UserLoginSchema)
def login_user(data: UserLoginSchema):
    try:
        current_app.logger.info('Login endpoint called')
        auth_service = AuthService()
        payload = auth_service.login(data.model_dump())
        return jsonify(payload), 200
    except ValidationError as e:
        current_app.logger.error(f'Validation error: {str(e)}')
        return jsonify({'error': 'validation error', 'details': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Internal server error: {e}')
        return jsonify({'error': f'internal server error {e}'}), 500

@auth_bp.route('/verify', methods = ["POST"])
def verify_user():
    data = request.get_json()
    # improvised validation
    if "token" not in data:
        return jsonify({"error": "token not provided"}), 400
    try:
        auth_service = AuthService()
        token = data.get('token')
        if not token:
            return jsonify({'error': 'token not provided'}), 400
        payload = auth_service.verify_token(token)
        return jsonify(payload), 200
    except Exception as e:
        current_app.logger.error(f'Internal server error: {e}')
        return jsonify({'error': f'internal server error {e}'}), 500

