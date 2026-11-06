import random
import csv
from datetime import datetime, timedelta

random.seed(42)

N = 2500
START = datetime(2026, 5, 1)
DAYS = 180

# category: (weight, mean resolution hours)
categories = {
    "Provisioning": (22, 40),
    "Billing": (20, 60),
    "Network Fault": (18, 26),
    "SIM Activation": (12, 10),
    "Porting": (10, 55),
    "Plan Change": (10, 14),
    "Number Allocation": (8, 20),
}
regions = ["North", "South", "East", "West", "Central"]
channels = ["Email", "Portal", "Phone", "Walk-in"]
priorities = ["Low", "Medium", "High", "Critical"]
agents = [f"Agent_{i:02d}" for i in range(1, 16)]

cat_names = list(categories)
cat_weights = [categories[c][0] for c in cat_names]

# messy variants to clean later
messy = {
    "Billing": ["billing", "BILLING", "Billing "],
    "Network Fault": ["network fault", "Network_Fault", "NETWORK FAULT"],
    "Provisioning": ["provisioning", "Provisionning"],
}

rows = []
for i in range(1, N + 1):
    cat = random.choices(cat_names, weights=cat_weights)[0]

    # weekdays and Mondays are busier
    day_offset = random.randint(0, DAYS - 1)
    created = START + timedelta(days=day_offset)
    while created.weekday() >= 5 and random.random() < 0.8:
        created = START + timedelta(days=random.randint(0, DAYS - 1))
    if random.random() < 0.15:
        while created.weekday() != 0:
            created = START + timedelta(days=random.randint(0, DAYS - 1))
    hour = int(min(max(random.gauss(11.5, 3), 8), 20))
    created = created.replace(hour=hour, minute=random.randint(0, 59), second=0)

    priority = random.choices(priorities, weights=[30, 45, 18, 7])[0]
    mean = categories[cat][1]
    factor = {"Low": 1.3, "Medium": 1.0, "High": 0.7, "Critical": 0.45}[priority]
    hours = max(0.5, random.lognormvariate(0, 0.6) * mean * factor)

    status = random.choices(["Closed", "Resolved", "Open", "Pending"], weights=[60, 25, 8, 7])[0]
    resolved = created + timedelta(hours=hours) if status in ("Closed", "Resolved") else None

    category_out = cat
    if cat in messy and random.random() < 0.08:
        category_out = random.choice(messy[cat])

    rows.append({
        "ticket_id": f"TKT{100000 + i}",
        "created_at": created.strftime(random.choice(["%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M"])) if random.random() < 0.03 else created.strftime("%Y-%m-%d %H:%M"),
        "resolved_at": resolved.strftime("%Y-%m-%d %H:%M") if resolved else "",
        "category": category_out,
        "priority": priority,
        "status": status,
        "region": random.choice(regions) if random.random() > 0.04 else "",
        "channel": random.choice(channels),
        "agent": random.choice(agents),
        "customer_type": random.choices(["Prepaid", "Postpaid", "Enterprise"], weights=[50, 35, 15])[0],
    })

# add some duplicates
rows += random.sample(rows, 40)
random.shuffle(rows)

with open("telecom_tickets.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {len(rows)} rows")
