from pymongo import read_concern, write_concern

from utils import transactional
from workloads.workload import Workload


class Workload_C(Workload):
    """
      100/0 read/update
      1000 records
      10000 operations
      :return:
    """

    def __init__(self, db, runners):
        records = 1000
        operations = 10000

        super().__init__(db, runners, records, operations)

    def __repr__(self):
        return "workload C"

    def benchmark_mongo3(self):
        for i in range(self.operations):
            self.num_read += 1
            self.collection.find_one({"item": i // 100})

        return (
            f"📖 Number of reads: {self.num_read}\n"
            + f"🔎 {(self.num_read / self.operations) * 100}% reads"
        )

    def benchmark_mongo4(self):
        rc = read_concern.ReadConcern("majority")
        wc = write_concern.WriteConcern("majority")
        batch_size = 5000
        print(f"Batch size: {batch_size}")

        with self.collection.database.client.start_session() as session:
            for i in range(int(self.operations / batch_size)):
                with session.start_transaction(read_concern=rc, write_concern=wc):
                    for j in range(batch_size):
                        self.num_read += 1
                        self.collection.find_one(
                            {"item": i * j // 100}, session=session
                        )

            return (
                f"📖 Number of reads: {self.num_read}\n"
                + f"🔎 {(self.num_read / self.operations) * 100}% reads"
            )

    @transactional
    def perform_operations(self, db, batch_size, i):
        for j in range(batch_size):
            self.num_read += 1
            self.collection.find_one({"item": i * j // 100})

    def benchmark_fdbdl(self):
        batch_size = 5000
        print(f"Batch size: {batch_size}")
        for i in range(int(self.operations / batch_size)):
            self.perform_operations(self.db, batch_size, i)
        return (
            f"📖 Number of reads: {self.num_read}\n"
            + f"🔎 {(self.num_read / self.operations) * 100}% reads"
        )
