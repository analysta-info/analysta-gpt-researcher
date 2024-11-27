import json
import re
import json_repair
from ..utils.llm import create_chat_completion
from ..prompts import auto_agent_instructions
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def choose_agent(
    query, cfg, parent_query=None, cost_callback: callable = None, headers=None
):
    """
    Chooses the agent automatically
    Args:
        parent_query: In some cases the research is conducted on a subtopic from the main query.
        The parent query allows the agent to know the main context for better reasoning.
        query: original query
        cfg: Config
        cost_callback: callback for calculating llm costs

    Returns:
        agent: Agent name
        agent_role_prompt: Agent role prompt
    """
    query = f"{parent_query} - {query}" if parent_query else f"{query}"
    response = None

    try:
        logger.info(f"Attempting to create chat completion for query: {query}")
        response = await create_chat_completion(
            model=cfg.smart_llm_model,
            messages=[
                {"role": "system", "content": f"{auto_agent_instructions()}"},
                {"role": "user", "content": f"task: {query}"},
            ],
            temperature=0.15,
            llm_provider=cfg.smart_llm_provider,
            llm_kwargs=cfg.llm_kwargs,
            cost_callback=cost_callback,
        )
        
        if response is None:
            logger.error("create_chat_completion returned None")
            return await fallback_agent()
            
        logger.info(f"Received response from create_chat_completion: {response}")

    except Exception as e:
        logger.error(f"Error in create_chat_completion: {str(e)}", exc_info=True)
        return await fallback_agent()

    try:
        logger.info("Attempting to parse response as JSON")
        agent_dict = json.loads(response)
        logger.info(f"Successfully parsed JSON: {agent_dict}")
        return agent_dict["server"], agent_dict["agent_role_prompt"]

    except Exception as e:
        logger.error(f"Error parsing JSON: {str(e)}", exc_info=True)
        return await handle_json_error(response)

async def handle_json_error(response):
    if not response:
        logger.error("Empty response received in handle_json_error")
        return await fallback_agent()
        
    try:
        logger.info("Attempting to repair JSON")
        agent_dict = json_repair.loads(response)
        if agent_dict.get("server") and agent_dict.get("agent_role_prompt"):
            logger.info("Successfully repaired JSON")
            return agent_dict["server"], agent_dict["agent_role_prompt"]
    except Exception as e:
        logger.error(f"Error using json_repair: {str(e)}", exc_info=True)

    logger.info("Attempting to extract JSON with regex")
    json_string = extract_json_with_regex(response)
    if json_string:
        try:
            json_data = json.loads(json_string)
            logger.info("Successfully extracted and parsed JSON with regex")
            return json_data["server"], json_data["agent_role_prompt"]
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding extracted JSON: {str(e)}", exc_info=True)

    logger.warning("All JSON parsing attempts failed, falling back to default agent")
    return await fallback_agent()

def extract_json_with_regex(response):
    try:
        json_match = re.search(r"{.*?}", response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return None
    except Exception as e:
        logger.error(f"Error in regex extraction: {str(e)}", exc_info=True)
        return None

async def fallback_agent():
    """Provides default agent configuration when all else fails"""
    logger.info("Using fallback agent configuration")
    return "Default Agent", (
        "You are an AI critical thinker research assistant. Your sole purpose is to write well written, "
        "critically acclaimed, objective and structured reports on given text."
    )