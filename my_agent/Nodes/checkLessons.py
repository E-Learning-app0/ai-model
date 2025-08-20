import redis
import json
import os
import logging
from my_agent.state import InputState, OutputState
import random
# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("agent-service")  # custom logger

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

def check_if_module_done(state: InputState) -> OutputState:
    
    logger.info("Trying to connect to Redis...")
    logger.info("REDIS_HOST=%s, REDIS_PORT=%s, PASSWORD_SET=%s", REDIS_HOST, REDIS_PORT, REDIS_PASSWORD is not None)
    module_id = random.randint(1, 100)
    logger.info(f"Checking module completion status for module_id={module_id}")

    try:
        redis_client.ping()
        logger.info("✅ Redis ping successful")
        # Check external forced done flag
        logger.info(f"Checking before start redis")
        forced_done = redis_client.get(f"module:{module_id}:forced_done")
        logger.info(f"Checking after start redis")
        if forced_done:
            logger.info("Module is forced done in Redis. Generate exams.")
            state["module_done"] = True
            state["generate_exam"] = True
            return state  # for exams
        
        logger.info("Module not forced done. Generate QCM.")
        # For testing: force exam generation
        state["module_done"] = False
        state["generate_exam"] = False
        return state  # for Exam testing
    except Exception as e:
        logger.error(f"Error checking module in Redis: {e}", exc_info=True)
        state["module_done"] = False
        state["generate_exam"] = False
        return state
