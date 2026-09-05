import sys
import os
from sqlalchemy import text
from database.session import SyncSessionLocal, sync_engine

def fix():
    session = SyncSessionLocal()
    # Update some bank transactions to be UNMATCHED
    session.execute(text("UPDATE transactions SET status = 'unmatched' WHERE source = 'HDFC' AND id % 7 = 0;"))
    session.commit()
    print("Fixed status for unmatched bank transactions.")

if __name__ == "__main__":
    fix()
