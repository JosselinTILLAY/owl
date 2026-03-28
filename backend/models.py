from typing import List, Optional
from pydantic import BaseModel

class Feature(BaseModel):
    id: str
    name: str
    description: str

class TextRequest(BaseModel):
    content: str

class PodcastScriptLine(BaseModel):
    speaker: str
    content: str

class PodcastScript(BaseModel):
    title: str
    lines: List[PodcastScriptLine]

class PodcastResponse(BaseModel):
    title: str
    audio_url: str
    script: List[PodcastScriptLine]
    duration_estimate: str
