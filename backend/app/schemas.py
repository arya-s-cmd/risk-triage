from pydantic import BaseModel, Field
from typing import Optional
class ComplaintIn(BaseModel):
    external_id: Optional[str]=None
    source: Optional[str]='portal'
    name: Optional[str]=None
    phone: Optional[str]=None
    email: Optional[str]=None
    ip: Optional[str]=None
    timestamp: Optional[str]=None
    text: Optional[str]=None
class ComplaintOut(ComplaintIn):
    id: int
    score: Optional[float]=None
    risk_band: Optional[str]=None
class SourceTrustIn(BaseModel):
    source: str
    trust: float = Field(ge=0.0, le=1.0)
class SourceTrustOut(SourceTrustIn):
    id: int
