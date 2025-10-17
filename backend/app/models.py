from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Float
from .db import Base
class Complaint(Base):
    __tablename__='complaints'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    external_id: Mapped[str|None]=mapped_column(String(64))
    source: Mapped[str|None]=mapped_column(String(64))
    name: Mapped[str|None]=mapped_column(String(256))
    phone: Mapped[str|None]=mapped_column(String(32))
    email: Mapped[str|None]=mapped_column(String(256))
    ip: Mapped[str|None]=mapped_column(String(64))
    timestamp: Mapped[str|None]=mapped_column(String(32))
    text: Mapped[str|None]=mapped_column(Text)
    score: Mapped[float|None]=mapped_column(Float)
    risk_band: Mapped[str|None]=mapped_column(String(16))
    explanation_json: Mapped[str|None]=mapped_column(Text)
class SourceTrust(Base):
    __tablename__='source_trust'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    source: Mapped[str]=mapped_column(String(64), unique=True)
    trust: Mapped[float]=mapped_column(Float)
