from flask import Blueprint, request, jsonify, current_app
from app.chatbot.graph_state import GraphState 
import app.chatbot.workflow as workflow
from app.core.validation_middleware import validate_json
from langchain_core.runnables import RunnableLambda

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/workflow', methods = ['POST'])
@validate_json(GraphState)
def run_workflow(data: GraphState):
    try:
        compiled_workflow = workflow.compiled_workflow
        result = compiled_workflow.invoke(data)
        result = result.model_dump()
        
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f'Error running workflow: {e}')
        return jsonify({'error': f'error running workflow, {e}'}), 500
