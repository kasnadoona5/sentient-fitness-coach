"""
Flask API for Sentient Fitness Coach Agent
Provides REST endpoints compatible with Sentient platform
"""

from flask import Flask, request, Response, jsonify
import asyncio
import json
import logging

from sentient_agent import sentient_fitness_agent

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET'])
def home():
    """
    Agent info endpoint (Sentient standard)
    """
    return jsonify(sentient_fitness_agent.get_info())

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint (Sentient standard)
    """
    return jsonify(sentient_fitness_agent.health_check())

@app.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint - Server-Sent Events streaming
    Compatible with Sentient Chat API
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'anonymous')
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        logger.info(f"Chat request from {user_id}: {message[:50]}...")
        
        def generate():
            """Generate SSE stream from async generator"""
            # Create new event loop for this request
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Create async generator
                async def async_stream():
                    async for chunk in sentient_fitness_agent.process_message(user_id, message):
                        yield f"data: {json.dumps({'content': chunk, 'type': 'chunk'})}\n\n"
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
                # Run the async generator and collect results
                async def collect_chunks():
                    chunks = []
                    async for chunk in sentient_fitness_agent.process_message(user_id, message):
                        chunks.append(f"data: {json.dumps({'content': chunk, 'type': 'chunk'})}\n\n")
                    chunks.append(f"data: {json.dumps({'type': 'done'})}\n\n")
                    return chunks
                
                # Execute and yield chunks
                chunks = loop.run_until_complete(collect_chunks())
                for chunk in chunks:
                    yield chunk
                    
            except Exception as e:
                logger.error(f"Streaming error: {e}", exc_info=True)
                yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"
            finally:
                loop.close()
        
        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
