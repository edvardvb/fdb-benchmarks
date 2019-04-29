import random
from pymongo import write_concern, read_concern

from workloads.workload import Workload
from constants import READ, INSERT
from utils import transactional



class Workload_D(Workload):
    """
      95/5 read/insert
      1000 records
      100000 operations
      :return:
    """

    def __init__(self, db, runners):
        records = 1000
        operations = 100000

        super().__init__(db, runners, records, operations)

    def __repr__(self):
        return 'workload D'

    def benchmark_mongo3(self):
        ops = random.choices([READ, INSERT], [95, 5], k=self.operations)
        for i, op in enumerate(ops):
            if op == READ:
                self.num_read += 1
                self.collection.find_one({'item': i // 100})

            elif op == INSERT:
                self.num_insert += 1
                self.collection.insert_one(
                    {
                        "item": self.records + i,
                        "qty": 100 + i,
                        "tags": ["cotton"],
                        "title": "How do I create manual workload i.e., Bulk inserts to Collection "
                    })
        return (
                f'📖 Number of reads: {self.num_read}\n' +
                f'✍️  Number of inserts: {self.num_insert}\n' +
                f'🔎 {(self.num_read / self.operations) * 100}% reads'
        )

    def benchmark_mongo4(self):
        rc = read_concern.ReadConcern('majority')
        wc = write_concern.WriteConcern('majority')
        batch_size = 5000
        print(f'Batch size: {batch_size}')

        with self.collection.database.client.start_session() as session:
            for i in range(int(self.operations/batch_size)):
                ops = random.choices([READ, INSERT], [95, 5], k=batch_size)
                with session.start_transaction(read_concern=rc, write_concern=wc):
                    for op in ops:
                        if op == READ:
                            self.num_read += 1
                            self.collection.find_one({'item': i // 100}, session=session)
                        elif op == INSERT:
                            self.num_insert += 1
                            self.collection.insert_one(
                                {
                                    "item": self.records + i,
                                    "qty": 100 + i,
                                    "tags": ["cotton"],
                                    "title": "How do I create manual workload i.e., Bulk inserts to Collection "
                                }, session=session)
            return (
                    f'📖 Number of reads: {self.num_read}\n' +
                    f'✍️  Number of inserts: {self.num_insert}\n' +
                    f'🔎 {(self.num_read / self.operations) * 100}% reads'
            )

    @transactional
    def perform_operations(self, db, ops, i):
        for op in ops:
            if op == READ:
                self.num_read += 1
                self.collection.find_one({'item': i // 100})
            elif op == INSERT:
                self.num_insert += 1
                self.collection.insert_one(
                    {
                        "item": self.records + i,
                        "qty": 100 + i,
                        "tags": ["cotton"],
                        "title": "How do I create manual workload i.e., Bulk inserts to Collection "
                    })

    def benchmark_fdbdl(self):
        batch_size = 5000
        print(f'Batch size: {batch_size}')
        for i in range(int(self.operations / batch_size)):
            ops = random.choices([READ, INSERT], [95, 5], k=batch_size)
            self.perform_operations(self.db, ops, i)
        return (
                f'📖 Number of reads: {self.num_read}\n' +
                f'✍️  Number of inserts: {self.num_insert}\n' +
                f'🔎 {(self.num_read / self.operations) * 100}% reads'
        )
