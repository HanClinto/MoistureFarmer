from typing import ClassVar
from pydantic import BaseModel

# Global config where all global settings are class variables
class GlobalConfig(BaseModel):
    """
    Global configuration for the simulation environment.
    This class holds configuration settings that can be accessed globally.
    """
    # Simulation settings
    simulation_speed: ClassVar[float] = 1.0  # Speed of the simulation (1.0 = real-time, >1.0 = faster, <1.0 = slower)
    max_log_entries: ClassVar[int] = 1000  # Maximum number of log entries to keep
    log_print_level: ClassVar[int] = 0  # Log level for printing (0 = info, 1 = warning, 2 = error)
 
    # Web request settings
    default_timeout: ClassVar[float] = 5.0  # Default timeout for web requests in seconds

    # LLM settings
    llm_model: ClassVar[str] = "gpt-3.5-turbo"  # Default LLM model to use
    llm_api_url: ClassVar[str] = "http://localhost:5000/v1/chat/completions"  # URL for the LLM API
    llm_temperature: ClassVar[float] = 0.7  # Temperature for LLM responses (0.0 = deterministic, 1.0 = more random)
    llm_top_p: ClassVar[float] = 1.0  # Top-p sampling for LLM responses (0.0 = no sampling, 1.0 = full sampling)
    llm_top_k: ClassVar[int] = 50  # Top-k sampling for LLM responses (0 = no top-k)
    llm_seed: ClassVar[int] = 42  # Seed for LLM random number generation

