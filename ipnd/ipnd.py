from ipnd import record
from typing import List
from datetime import datetime


class IPND:
    def __init__(self, source: str, seq: int, count: int = None, date: datetime = None):
        self.source = source
        self.seq = seq
        self.count = count
        self.date = date
        self.transactions: List[record.Transaction] = []

    def add_transaction(self, transaction: record.Transaction):
        self.transactions.append(transaction)

    def generate(self):
        return (
            [record.Header(source=self.source, seq=self.seq, date=self.date).generate()]
            + [t.generate() for t in self.transactions]
            + [
                record.Footer(
                    source=self.source,
                    seq=self.seq,
                    count=len(self.transactions),
                    date=self.date,
                ).generate()
            ]
        )

    def generate_to_string(self):
        return "".join(["".join(x) for x in self.generate()])
