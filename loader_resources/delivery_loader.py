import csv
from collections import defaultdict

class Delivery:
    def __init__(
        self,
        id,
        medicine_name,
        quantity,
        total_weight,
        city,
        location_name,
        priority
    ):
        self.id = int(id)
        self.medicine_name = medicine_name
        self.quantity = int(quantity)
        self.total_weight = float(total_weight)
        self.city = city.strip()
        self.location_name = location_name
        self.priority = int(priority)


def load_deliveries(path: str):
    deliveries = []

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            deliveries.append(
                Delivery(
                    row["id"],
                    row["medicine_name"],
                    row["quantity"],
                    row["total_weight"],
                    row["city"],
                    row["location_name"],
                    row["priority"]
                )
            )

    return deliveries
