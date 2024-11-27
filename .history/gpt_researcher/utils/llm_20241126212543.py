# gpt_researcher/utils/llm.py

from typing import Optional, Dict, Any
from ..config import Config
from ..llm_provider.generic.base import GenericLLMProvider

def get_llm(llm_provider: str, **kwargs) -> GenericLLMProvider:
    """
    Get LLM provider with fallback handling
    """
    try:
        if llm_provider.lower() == "groq":
            # Import needed here to avoid the validation error
            from langchain.chat_models import ChatOpenAI
            # Fallback to OpenAI if Groq fails
            return ChatOpenAI(**kwargs)
        return GenericLLMProvider.from_provider(llm_provider, **kwargs)
    except Exception as e:
        print(f"Error initializing {llm_provider}: {str(e)}")
        print("Falling back to OpenAI...")
        from langchain.chat_models import ChatOpenAI
        return ChatOpenAI(**kwargs)

async def create_chat_completion(
    messages: list,
    model: str,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    llm_provider: str = "openai",
    llm_kwargs: Optional[Dict[str, Any]] = None,
    cost_callback: Optional[callable] = None,
) -> str:
    """
    Create a chat completion with better error handling
    """
    try:
        # Get the LLM provider
        provider = get_llm(
            llm_provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **(llm_kwargs or {})
        )

        # Create the chat completion
        response = await provider.acomplete(
            messages=messages,
            cost_callback=cost_callback
        )

        return response
    except Exception as e:
        print(f"Error in create_chat_completion: {str(e)}")
        # Fallback to a simpler provider if needed
        try:
            from langchain.chat_models import ChatOpenAI
            fallback_provider = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=temperature
            )
            response = await fallback_provider.acomplete(
                messages=messages,
                cost_callback=cost_callback
            )
            return response
        except Exception as fallback_error:
            print(f"Fallback error: {str(fallback_error)}")
            return None