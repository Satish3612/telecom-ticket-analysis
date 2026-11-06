import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------- STEP 1: Load ----------
df = pd.read_csv("telecom_tickets.csv")
print("Rows pehle:", len(df))
print(df.info())

# ---------- STEP 2: Clean ----------
# 2a. Duplicates hatao
print("Duplicates:", df.duplicated().sum())
df = df.drop_duplicates()

# 2b. Category names theek karo
df["category"] = (
    df["category"]
    .str.strip()
    .str.lower()
    .str.replace("_", " ", regex=False)
    .replace({"provisionning": "provisioning"})
    .str.title()
)
print(df["category"].value_counts())

# 2c. Dates theek karo (do formats hain)
iso = pd.to_datetime(df["created_at"], format="%Y-%m-%d %H:%M", errors="coerce")
dmy = pd.to_datetime(df["created_at"], format="%d/%m/%Y %H:%M", errors="coerce")
df["created_at"] = iso.fillna(dmy)
df["resolved_at"] = pd.to_datetime(df["resolved_at"], format="%Y-%m-%d %H:%M", errors="coerce")
print("Bad created_at:", df["created_at"].isna().sum())

# 2d. Missing region
df["region"] = df["region"].fillna("Unknown").replace("", "Unknown")

# 2e. Resolution time (sirf resolved/closed tickets ke liye)
df["resolution_hours"] = (df["resolved_at"] - df["created_at"]).dt.total_seconds() / 3600
done = df.dropna(subset=["resolution_hours"]).copy()
print("Rows ab:", len(df), "| Resolved rows:", len(done))

# ---------- STEP 3: 5 Questions ----------
print("\nQ1. Tickets per category")
print(df["category"].value_counts())

print("\nQ2. Avg resolution time (hours) per category")
avg_res = done.groupby("category")["resolution_hours"].mean().sort_values(ascending=False)
print(avg_res.round(1))

print("\nQ3a. Busiest weekday")
df["weekday"] = df["created_at"].dt.day_name()
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
print(df["weekday"].value_counts().reindex(order))
print("\nQ3b. Busiest hour")
print(df["created_at"].dt.hour.value_counts().sort_index())

print("\nQ4. SLA breach % (> 48 hours)")
done["sla_breach"] = done["resolution_hours"] > 48
print(round(done["sla_breach"].mean() * 100, 1), "%")
print(done.groupby("category")["sla_breach"].mean().mul(100).round(1).sort_values(ascending=False))

print("\nQ5. Top 3 delay categories")
print(avg_res.head(3).round(1))

# ---------- STEP 4: Charts ----------
df["category"].value_counts().plot(kind="bar", title="Tickets by Category")
plt.ylabel("Tickets"); plt.tight_layout(); plt.savefig("chart1_category.png"); plt.clf()

df.set_index("created_at").resample("W").size().plot(title="Weekly Ticket Volume")
plt.ylabel("Tickets"); plt.tight_layout(); plt.savefig("chart2_weekly.png"); plt.clf()

done["resolution_hours"].plot(kind="hist", bins=40, title="Resolution Time Distribution")
plt.axvline(48, color="red", linestyle="--", label="SLA 48h"); plt.legend()
plt.xlabel("Hours"); plt.tight_layout(); plt.savefig("chart3_hist.png"); plt.clf()

avg_res.plot(kind="barh", title="Avg Resolution Hours by Category")
plt.xlabel("Hours"); plt.tight_layout(); plt.savefig("chart4_avg_res.png"); plt.clf()

# ---------- Cleaned file save ----------
df.to_csv("telecom_tickets_clean.csv", index=False)
print("\nDone: 4 charts + telecom_tickets_clean.csv saved")
