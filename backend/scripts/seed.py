from app.db.session import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.bank import BankProvider
from app.models.user import User
import app.models

Base.metadata.create_all(bind=engine)

db = SessionLocal()

user = db.query(User).filter(User.email == "demo@example.com").first()
if not user:
    db.add(
        User(
            full_name="Demo User",
            email="demo@example.com",
            hashed_password=hash_password("demo-password"),
            is_active=True,
        )
    )

provider = db.query(BankProvider).filter(BankProvider.code == "TIMO").first()
if not provider:
    db.add(
        BankProvider(
            code="TIMO",
            name="Timo",
            provider_type="digital_bank",
            status="available",
            supported_scopes=["accounts:read", "transactions:read", "balance:read"],
        )
    )

db.commit()
db.close()

print("Seed completed")
