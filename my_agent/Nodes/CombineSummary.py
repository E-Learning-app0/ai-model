import redis
from my_agent.state import InputState, OutputState

# Initialize Redis connection (adjust parameters as needed)
import redis
import json
import os

# Redis connection with environment variable support
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Create Redis connection with Azure Redis Cache support
if REDIS_PASSWORD:
    redis_client = redis.Redis(
        host=REDIS_HOST, 
        port=REDIS_PORT, 
        db=0,
        password=REDIS_PASSWORD,
        ssl=True,
        ssl_check_hostname=False,
        ssl_cert_reqs=None
    )
else:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def combine_all_summaries(state: InputState) -> OutputState:
    module_id = state.get("module_id") or "test_module"
    if not module_id:
        raise ValueError("Missing module_id in state")

    # Redis key pattern for lesson summaries of this module
    # Assuming you store lesson summaries per lesson, with keys like 'lesson:{lesson_id}:summary'
    # And you have a Redis Set or List holding all lesson IDs for the module under 'module:{module_id}:lessons'
    lesson_ids_key = f"module:{module_id}:lessons"
    lesson_ids = redis_client.smembers(lesson_ids_key)  # set of bytes

    combined_summary = ""

    for lesson_id_bytes in lesson_ids:
        lesson_id = lesson_id_bytes.decode('utf-8')
        summary_key = f"lesson:{lesson_id}:summary"
        summary_bytes = redis_client.get(summary_key)
        if summary_bytes:
            combined_summary += summary_bytes.decode('utf-8') + "\n\n"

    if not combined_summary:
        # If no summaries found in Redis, use the current lesson_text from state
        combined_summary = state.get("lesson_text", "No content available for exam generation.")
        print(f"Using current lesson_text for module {module_id}")

    print(f"Combined summary for module {module_id} length: {len(combined_summary)}")

    # Return combined summary in 'lesson_text' so generate_exam can use it
    return {"lesson_text": combined_summary.strip()}
