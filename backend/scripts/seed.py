from app.db.session import Base, SessionLocal, engine
from app.models.domain import BankProvider, User

Base.metadata.create_all(bind=engine)

db = SessionLocal()

user = db.query(User).filter(User.email == "demo@pfai.local").first()
if not user:
    db.add(User(full_name="Demo User", email="demo@pfai.local"))

provider = db.query(BankProvider).filter(BankProvider.code == "BANK_A").first()
if not provider:
    db.add(BankProvider(code="BANK_A", name="Bank A Sandbox"))

db.commit()
db.close()

print("Seed completed")
