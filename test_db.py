import time
from database.session import SyncSessionLocal
from database.models import Transaction

db = SyncSessionLocal()
t0 = time.time()
t = db.query(Transaction).first()
t1 = time.time()
print(f"first() took {t1-t0:.4f}s")
