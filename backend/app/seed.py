from sqlalchemy.orm import Session
from .db import Base, engine, SessionLocal
from .models import Complaint, SourceTrust
from datetime import datetime, timedelta
import random
from .utils import norm_phone, norm_email
N=200
NAMES=['Rahul','Priya','Anil','Sunita','Vikram','Aisha','Rohit','Neha']
SOURCES=['portal','hotline','email','partner','api']
KEY_TEXTS=['KYC OTP asked; bank card compromised','UPI fraud link sent via SMS','Sextortion email demanding payment','Fake customs duty call (FedEx)','Income tax refund phishing','Loan app harassment and threats','Card CVV requested by caller','Password reset scam']
PHONES=['+91 98{:08d}'.format(10000000+i) for i in range(500)]
EMAILS=['user{}@mail.com'.format(i) for i in range(500)]
IPS=['10.0.{}.{}'.format(i//255,i%255) for i in range(1,500)]

def seed():
    Base.metadata.create_all(bind=engine)
    db: Session=SessionLocal()
    if db.query(Complaint).count()==0:
        rnd=random.Random(42)
        now=datetime.utcnow()
        for i in range(N):
            name=rnd.choice(NAMES)+' '+str(rnd.randint(1,99))
            src=rnd.choice(SOURCES)
            phone=norm_phone(rnd.choice(PHONES) if rnd.random()<0.8 else None)
            email=norm_email(rnd.choice(EMAILS) if rnd.random()<0.7 else None)
            ip=rnd.choice(IPS) if rnd.random()<0.5 else None
            ts=(now - timedelta(days=rnd.randint(0,30), hours=rnd.randint(0,23))).replace(microsecond=0).isoformat()
            txt=rnd.choice(KEY_TEXTS) if rnd.random()<0.7 else 'General complaint about suspicious activity'
            c=Complaint(external_id=f'EXT-{i}', source=src, name=name, phone=phone, email=email, ip=ip, timestamp=ts, text=txt)
            db.add(c)
        for s,t in [('portal',0.5),('hotline',0.4),('email',0.6),('partner',0.3),('api',0.7)]:
            if not db.query(SourceTrust).filter(SourceTrust.source==s).one_or_none():
                db.add(SourceTrust(source=s, trust=t))
        db.commit()
    db.close()

if __name__=='__main__':
    seed()
