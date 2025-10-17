from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
import json, math
from .models import Complaint, SourceTrust
KEYWORDS=['otp','kyc','upi','fraud','sextortion','ransom','loan app','fedex','customs','income tax','refund','cvv','password','bank','pin','block','freeze']

def now_utc():
    return datetime.now(timezone.utc)

def days_ago(ts):
    if not ts: return 9999.0
    try:
        dt=datetime.fromisoformat(ts.replace('Z',''))
        return max(0.0,(now_utc()-dt.replace(tzinfo=timezone.utc)).total_seconds()/86400.0)
    except Exception:
        return 9999.0

def keyword_hits(text):
    if not text: return 0
    t=text.lower()
    return sum(1 for kw in KEYWORDS if kw in t)

def score_record(db: Session, c: Complaint):
    dup_phone = db.execute(text("SELECT COUNT(*) FROM complaints WHERE phone=:v AND id!=:id AND timestamp>=date('now','-90 day')"),{"v":c.phone,"id":c.id}).scalar() if c.phone else 0
    dup_email = db.execute(text("SELECT COUNT(*) FROM complaints WHERE email=:v AND id!=:id AND timestamp>=date('now','-90 day')"),{"v":c.email,"id":c.id}).scalar() if c.email else 0
    dup_ip = db.execute(text("SELECT COUNT(*) FROM complaints WHERE ip=:v AND id!=:id AND timestamp>=date('now','-90 day')"),{"v":c.ip,"id":c.id}).scalar() if c.ip else 0
    days=days_ago(c.timestamp)
    recency=max(0.0,1.0-min(days,30.0)/30.0)
    recent_similar=(dup_phone+dup_email+dup_ip)
    k_hits=keyword_hits(c.text)
    trust=0.5
    if c.source:
        t=db.query(SourceTrust).filter(SourceTrust.source==c.source).one_or_none()
        if t: trust=float(t.trust)
    w_dup,w_kw,w_rec,w_src=0.35,0.25,0.20,0.20
    dup_signal=math.tanh(recent_similar/3.0)
    score=(w_dup*dup_signal)+(w_kw*min(k_hits/3.0,1.0))+(w_rec*recency)+(w_src*(1.0-trust))
    band='low'
    if score>=0.75: band='critical'
    elif score>=0.55: band='high'
    elif score>=0.35: band='medium'
    exp={"dup_signal":dup_signal,"dup_counts":{"phone":dup_phone,"email":dup_email,"ip":dup_ip},"keywords":k_hits,"recency_days":days,"recency_score":recency,"source":c.source,"source_trust":trust,"weights":{"dup":w_dup,"kw":w_kw,"rec":w_rec,"src":w_src}}
    return float(round(score,4)), exp
