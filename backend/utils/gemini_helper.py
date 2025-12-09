"""
Gemini API Helper Utilities
Provides centralized model creation and error handling for Gemini API
"""
import google.generativeai as genai
from typing import Optional
import time


def create_gemini_model(
    api_key: str, 
    model_name: Optional[str] = None,
    fallback_models: Optional[list] = None
):
    """
    Create a Gemini model with fallback support
    
    Args:
        api_key: Gemini API key
        model_name: Primary model to use (default: gemini-1.5-flash)
        fallback_models: List of fallback models to try if primary fails
    
    Returns:
        GenerativeModel instance
    """
    if not api_key:
        raise ValueError("Gemini API key is required")
    
    genai.configure(api_key=api_key)
    
    # Default models in order of preference for free tier
    if fallback_models is None:
        fallback_models = [
            "models/gemini-2.5-flash",      # Latest stable flash model
            "models/gemini-flash-latest",   # Latest flash alias
            "models/gemini-pro-latest",     # Latest pro alias
        ]
    
    # Primary model
    if model_name:
        models_to_try = [model_name] + fallback_models
    else:
        models_to_try = fallback_models
    
    # Try each model
    last_error = None
    for model in models_to_try:
        try:
            return genai.GenerativeModel(model)
        except Exception as e:
            last_error = e
            continue
    
    # If all models fail, raise the last error
    if last_error:
        raise last_error
    
    # Default fallback
    return genai.GenerativeModel("models/gemini-2.5-flash")


def generate_with_retry(
    model, 
    prompt: str,
    max_retries: int = 3,
    initial_delay: float = 1.0
):
    """
    Generate content with automatic retry on quota errors
    
    Args:
        model: Gemini GenerativeModel instance
        prompt: The prompt to send
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds (doubles with each retry)
    
    Returns:
        Generated response
        
    Raises:
        Exception: If all retries are exhausted
    """
    delay = initial_delay
    last_error = None
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response
        except Exception as e:
            error_msg = str(e).lower()
            last_error = e
            
            # Check if it's a quota error
            if "quota" in error_msg or "429" in error_msg or "rate limit" in error_msg:
                if attempt < max_retries - 1:
                    print(f"⚠️ Quota exceeded, retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    continue
            
            # For other errors, fail immediately
            raise
    
    # If we exhausted all retries, raise the last error
    raise last_error


def get_quota_friendly_message(error: Exception) -> str:
    """
    Convert quota error to user-friendly message
    
    Args:
        error: The exception that occurred
    
    Returns:
        User-friendly error message
    """
    error_msg = str(error)
    
    if "quota" in error_msg.lower() or "429" in error_msg:
        return (
            "⚠️ Gemini API quota limit reached. "
            "Please try again later or upgrade to a paid plan. "
            "Free tier limits: 15 requests/minute, 1500 requests/day."
        )
    
    if "rate limit" in error_msg.lower():
        return "⚠️ Rate limit exceeded. Please wait a moment and try again."
    
    if "invalid api key" in error_msg.lower() or "authentication" in error_msg.lower():
        return "❌ Invalid API key. Please check your Gemini API key configuration."
    
    return f"❌ Gemini API error: {str(error)[:200]}"
