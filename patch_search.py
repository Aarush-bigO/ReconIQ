import re

with open("apps/api/routers/transactions.py", "r") as f:
    content = f.read()

new_sig = """async def list_transactions(
    source: str = "",
    status: str = "",
    search: str = "",
    page: int = 1,
    page_size: int = 50,
):"""

content = re.sub(r'async def list_transactions\([\s\S]*?page_size: int = 50,\n\):', new_sig, content)

new_logic = """        query = db.query(Transaction)
        if source:
            query = query.filter(Transaction.source == source)
        if status:
            query = query.filter(Transaction.status == status)
        if search:
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    Transaction.canonical_id.ilike(f"%{search}%"),
                    Transaction.payment_id.ilike(f"%{search}%"),
                    Transaction.order_id.ilike(f"%{search}%"),
                    Transaction.settlement_id.ilike(f"%{search}%"),
                    Transaction.utr.ilike(f"%{search}%")
                )
            )"""

content = re.sub(r'        query = db\.query\(Transaction\)[\s\S]*?query\.filter\(Transaction\.status == status\)', new_logic, content)

with open("apps/api/routers/transactions.py", "w") as f:
    f.write(content)
