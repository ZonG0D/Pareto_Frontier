from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Union

class ModelTierConfig(BaseModel):
    endpoint: str
    model: str
    timeout: int = 30
    retry_count: int = 2

class ParsingConfig(BaseModel):
    cleaned_key: str = "cleaned_text"
    semantic_helper: str = "semantic_helper"

class ConfigDefaults(BaseModel):
    ollama_fallback: str = "http://localhost:11434/api/chat"

class TieredConfig(BaseModel):
    cheap: ModelTierConfig
    smart: ModelTierConfig

class FullConfig(BaseModel):
    tiers: TieredConfig
    parsing: ParsingConfig
    defaults: ConfigDefaults
