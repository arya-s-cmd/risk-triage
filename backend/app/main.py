from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .db import engine, Base, get_db
from .models import Complaint, SourceTrust
from .schemas import ComplaintIn, ComplaintOut, SourceTrustIn, SourceTrustOut
from .utils import norm_phone, norm_email, iso_datetime
from .scoring import score_record
import json
app=FastAPI(title='Risk Scoring API')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
@app.on_event('startup')
def startup():
    Base.metadata.create_all(bind=engine)
@app.post('/ingest', response_model=ComplaintOut)
def ingest(payload: ComplaintIn, db: Session=Depends(get_db)):
    c=Complaint(external_id=payload.external_id, source=(payload.source or 'portal'), name=payload.name or None, phone=norm_phone(payload.phone), email=norm_email(payload.email), ip=payload.ip or None, timestamp=iso_datetime(payload.timestamp), text=payload.text or None)
    db.add(c); db.commit(); db.refresh(c)
    return ComplaintOut(id=c.id, **payload.model_dump(), score=c.score, risk_band=c.risk_band)
@app.post('/score/run')
def run_scoring(db: Session=Depends(get_db)):
    rows=db.query(Complaint).all()
    for c in rows:
        s, exp=score_record(db,c)
        c.score=s
        c.risk_band='critical' if s>=0.75 else 'high' if s>=0.55 else 'medium' if s>=0.35 else 'low'
        c.explanation_json=json.dumps(exp, separators=(',',':'), sort_keys=True)
    db.commit(); return {'ok':True,'scored':len(rows)}
@app.get('/queue', response_model=list[ComplaintOut])
def queue(limit:int=50, band:str|None=None, db: Session=Depends(get_db)):
    q=db.query(Complaint)
    if band: q=q.filter(Complaint.risk_band==band)
    rows=q.order_by(Complaint.score.desc().nullslast()).limit(min(limit,200)).all()
    return [ComplaintOut(id=r.id, external_id=r.external_id, source=r.source, name=r.name, phone=r.phone, email=r.email, ip=r.ip, timestamp=r.timestamp, text=r.text, score=r.score, risk_band=r.risk_band) for r in rows]
@app.get('/explain/{cid}')
def explain(cid:int, db: Session=Depends(get_db)):
    c=db.get(Complaint, cid)
    if not c: raise HTTPException(404,'not found')
    return {'id':c.id,'score':c.score,'band':c.risk_band,'explanation':json.loads(c.explanation_json or '{}')}
@app.get('/sources', response_model=list[SourceTrustOut])
def list_sources(db: Session=Depends(get_db)):
    rows=db.query(SourceTrust).order_by(SourceTrust.source.asc()).all()
    return [SourceTrustOut(id=r.id, source=r.source, trust=r.trust) for r in rows]
@app.put('/sources', response_model=SourceTrustOut)
def upsert_source(payload: SourceTrustIn, db: Session=Depends(get_db)):
    row=db.query(SourceTrust).filter(SourceTrust.source==payload.source).one_or_none()
    if row: row.trust=payload.trust
    else:
        row=SourceTrust(source=payload.source, trust=payload.trust); db.add(row)
    db.commit(); db.refresh(row); return SourceTrustOut(id=row.id, source=row.source, trust=row.trust)
