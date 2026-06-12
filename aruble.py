import json
import base64
import random
import logging

logger = logging.getLogger(__name__)

async def process_aruble_captcha(base64_payload: str) -> str:
    """
    Decodes an incoming Base64 JSON challenge from Aruble Faucet,
    extracts parameters, generates accurate puzzle answers structurally,
    and returns a Base64 encoded payload matching the exact destination format.
    """
    try:
        # Step 1: Decode incoming Base64 package string into JSON Dictionary
        decoded_bytes = base64.b64decode(base64_payload)
        captcha_str = decoded_bytes.decode('utf-8')
        captcha = json.loads(captcha_str)
        
        ctype = captcha.get('type')
        key = captcha.get('key')
        answer = None

        # Step 2: Extract captcha variables based on target layout requirements
        if ctype == 'icon_order':
            # Map structural IDs matching token sequences prompted inside target layout
            answer_list = [
                item['id'] 
                for p in captcha.get('prompt', []) 
                for item in captcha.get('display', []) 
                if item['icon'] == p
            ]
            answer = json.dumps(answer_list)

        elif ctype == 'least_repeat':
            # Identify single isolated instances occurring lowest across target matrices
            grid = captcha.get('grid', [])
            counts = {}
            for item in grid:
                counts[item['icon']] = counts.get(item['icon'], 0) + 1
            
            least_icon = min(counts, key=counts.get)
            
            # Extract tracking ID parameters tied strictly onto the calculated minimum occurrence
            answer = next((item['id'] for item in grid if item['icon'] == least_icon), grid[0]['id'])

        elif ctype == 'slide':
            # Forward the precise requested percentage metrics required by the slider
            answer = str(captcha.get('target_pct', 50))

        else:
            # Handle unknown captcha schemas gracefully
            error_resp = json.dumps({"success": False, "error": f"Unknown captcha schema mapped: {ctype}"})
            return base64.b64encode(error_resp.encode('utf-8')).decode('utf-8')

        # Step 3: Bundle components into exact format required by Aruble Bot submission
        # Generates a random realistic execution timeframe mimicking manual interaction delays
        response_data = {
            "key": key,
            "answer": answer,
            "solve_time": str(random.randint(2500, 5500))
        }
        
        # Step 4: Stream final structural JSON array strings safely back into Base64
        response_json = json.dumps(response_data)
        base64_answer = base64.b64encode(response_json.encode('utf-8')).decode('utf-8')
        return base64_answer

    except Exception as e:
        logger.error(f"Aruble Cloud Solver Interruption: {str(e)}")
        err_data = json.dumps({"success": False, "error": str(e)})
        return base64.b64encode(err_data.encode('utf-8')).decode('utf-8')

