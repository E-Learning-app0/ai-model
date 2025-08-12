import redis
from my_agent.state import InputState, OutputState

# Initialize Redis connection (adjust as needed)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def check_if_module_done(state: InputState) -> OutputState:
    module_id = state.get("module_id")

    # Check external forced done flag
    forced_done = redis_client.get(f"module:{module_id}:forced_done")
    if forced_done:
        state["module_done"] = True
        state["generate_exam"] = True
        return state #for exams
    
    # For testing: force exam generation
    # Set module_done = True to trigger exam generation path
    state["module_done"] = True
    state["generate_exam"] = True
    return state #for Exam testing