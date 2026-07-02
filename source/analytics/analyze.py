import pandas as pd, numpy as np, re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data") + os.sep       # data/dispatch.csv + data/service.csv
OUT = os.path.join(HERE, "metrics.json")

disp = pd.read_csv(D+"dispatch.csv", dtype=str, keep_default_na=False)
serv = pd.read_csv(D+"service.csv", dtype=str, keep_default_na=False)
for df in (disp, serv):
    for c in df.columns: df[c] = df[c].astype(str).str.strip()

# ---------- REVENUE PARSE (from SERVICE item list) ----------
def parse_total(t):
    m = re.search(r'Total:\s*\$?\s*([\d,]+\.\d{2})', t)
    return float(m.group(1).replace(',','')) if m else np.nan

item_re = re.compile(r'([A-Za-z][A-Za-z0-9 \-\/&]*?)\s*\(Amount:\s*([\d.]+)\s*USD,\s*Quantity:\s*(\d+)')
def parse_items(t):
    out=[]
    for name,amt,qty in item_re.findall(t):
        out.append((name.strip(), float(amt), int(qty)))
    return out

serv["total"] = serv["Summer Storage Item List"].apply(parse_total)
serv["items"] = serv["Summer Storage Item List"].apply(parse_items)

paid = serv[serv["total"]>0]
zero = serv[(serv["total"]==0)]
nan_total = serv[serv["total"].isna()]

# item catalog
cat={}
for items in serv["items"]:
    for name,amt,qty in items:
        d=cat.setdefault(name,{"unit_prices":[],"qty":0,"revenue":0.0,"orders":0})
        d["unit_prices"].append(amt); d["qty"]+=qty; d["revenue"]+=amt*qty; d["orders"]+=1
catalog=[]
for name,d in cat.items():
    catalog.append({"item":name,"unit_price":round(float(np.median(d["unit_prices"])),2),
                    "total_qty":d["qty"],"revenue":round(d["revenue"],2),"orders":d["orders"]})
catalog.sort(key=lambda x:-x["revenue"])

# revenue by service type
rev_by_service = serv[serv["total"]>0].groupby("Service Type")["total"].agg(["sum","count","mean"]).round(2)

# ---------- DATES ----------
serv["subdate"] = pd.to_datetime(serv["Submission Date"], errors="coerce")
serv["evdate"]  = pd.to_datetime(serv["Date"].str.replace(r'\s+\d{1,2}:\d{2}\s*(AM|PM)$','',regex=True), errors="coerce")
disp["date"]    = pd.to_datetime(disp["Date"].replace("(no date)",""), errors="coerce")

serv_daily = serv.dropna(subset=["subdate"]).groupby(serv["subdate"].dt.date).size()
disp_daily = disp.dropna(subset=["date"]).groupby(disp["date"].dt.date).size()

# revenue by day (submission date)
serv_ok = serv.dropna(subset=["subdate"])
rev_daily = serv_ok[serv_ok["total"]>0].groupby(serv_ok["subdate"].dt.date)["total"].sum()

# ---------- OPERATIONS ----------
status = disp["Status"].replace("","(blank)").value_counts()
dstatus = disp["Dispatch Status"].replace("","(blank)").value_counts()
service_mix = disp["Service"].replace("","(blank)").value_counts()
buildings = disp["Building"].replace("","(blank)").value_counts()

complete = int((disp["Status"]=="Complete").sum())
completion_rate = round(100*complete/len(disp),1)
not_dispatched = int((disp["Dispatch Status"]=="Not Dispatched").sum())
queued = int((disp["Status"]=="Queued").sum())
issues = int((disp["Status"]=="Issue").sum())

# ---------- DATA QUALITY ----------
dq = {
 "dispatch_no_date": int((disp["Date"]=="(no date)").sum()),
 "dispatch_building_unknown": int(disp["Building"].str.contains("DON'T KNOW", case=False, na=False).sum()),
 "dispatch_blank_room": int((disp["Room"]=="").sum()),
 "dispatch_blank_phone": int((disp["Phone"]=="").sum()),
 "service_blank_order": int((serv["Order#:"]=="").sum()),
 "service_blank_invoice": int((serv["Invoice ID"]=="").sum()),
 "service_zero_total": int((serv["total"]==0).sum()),
 "service_no_total": int(serv["total"].isna().sum()),
}

metrics = {
 "counts": {"dispatch_rows":len(disp), "service_rows":len(serv),
            "orders_with_revenue":int(len(paid)), "orders_zero_total":int(len(zero)),
            "orders_no_total":int(len(nan_total))},
 "revenue": {
    "total": round(float(paid["total"].sum()),2),
    "aov_mean": round(float(paid["total"].mean()),2),
    "aov_median": round(float(paid["total"].median()),2),
    "max_order": round(float(paid["total"].max()),2),
    "by_service_type": {k:{"sum":round(float(v["sum"]),2),"count":int(v["count"]),"mean":round(float(v["mean"]),2)}
                         for k,v in rev_by_service.to_dict("index").items()},
    "value_buckets": {}
 },
 "catalog": catalog,
 "operations": {
    "completion_rate": completion_rate, "complete":complete,
    "queued":queued, "issues":issues, "not_dispatched":not_dispatched,
    "status": status.to_dict(), "dispatch_status": dstatus.to_dict(),
    "service_mix": service_mix.head(12).to_dict(),
    "buildings_top": buildings.head(15).to_dict(),
 },
 "dates": {
    "serv_min": str(serv["subdate"].min().date()) if serv["subdate"].notna().any() else None,
    "serv_max": str(serv["subdate"].max().date()) if serv["subdate"].notna().any() else None,
    "serv_daily": {str(k):int(v) for k,v in serv_daily.items()},
    "disp_daily": {str(k):int(v) for k,v in disp_daily.items()},
    "rev_daily": {str(k):round(float(v),2) for k,v in rev_daily.items()},
 },
 "data_quality": dq,
}
# value buckets
b=[0,50,100,150,200,300,10000]; lbls=["<$50","$50-100","$100-150","$150-200","$200-300","$300+"]
cut=pd.cut(paid["total"],bins=b,labels=lbls,right=False)
metrics["revenue"]["value_buckets"]={k:int(v) for k,v in cut.value_counts().reindex(lbls).fillna(0).items()}

# ---------- CONSULTANT INSIGHTS ----------
total_rev = metrics["revenue"]["total"]
box_rev = next((c["revenue"] for c in catalog if c["item"]=="UTrucking Box"),0)
box_qty = next((c["total_qty"] for c in catalog if c["item"]=="UTrucking Box"),0)
box_orders = next((c["orders"] for c in catalog if c["item"]=="UTrucking Box"),0)
zero_by_service = serv[serv["total"]==0]["Service Type"].replace("","(blank)").value_counts().to_dict()
ss_zero = int((serv[(serv["Service Type"]=="Summer Storage") & (serv["total"]==0)]).shape[0])
rev_sorted = sorted(rev_daily.tolist(), reverse=True)
peak5_share = round(100*sum(rev_sorted[:5])/max(sum(rev_sorted),1),1)
items_per_order = paid["items"].apply(lambda L: sum(q for _,_,q in L))
metrics["insights"] = {
  "box_revenue_share": round(100*box_rev/max(total_rev,1),1),
  "box_attach_rate": round(100*box_orders/max(len(paid),1),1),
  "avg_items_per_order": round(float(items_per_order.mean()),1),
  "peak5_revenue_share": peak5_share,
  "zero_by_service": {k:int(v) for k,v in zero_by_service.items()},
  "summer_storage_zero_leakage": ss_zero,
  "leakage_est_dollars": round(ss_zero*metrics["revenue"]["aov_median"],0),
  "box_price_scenarios": {f"+${k}": int(box_qty*k) for k in (1,2,3,5)},
  "not_dispatched_pct": round(100*not_dispatched/len(disp),1),
}

json.dump(metrics, open(OUT,"w"), indent=2, default=str)
print("INSIGHTS:", json.dumps(metrics["insights"], indent=2))

# ---------- PRINT SUMMARY ----------
m=metrics
print("REVENUE total = ${:,.2f}  | orders w/ revenue={}  zero-total={}  no-total={}".format(
    m["revenue"]["total"], m["counts"]["orders_with_revenue"], m["counts"]["orders_zero_total"], m["counts"]["orders_no_total"]))
print("AOV mean=${}  median=${}  max=${}".format(m["revenue"]["aov_mean"],m["revenue"]["aov_median"],m["revenue"]["max_order"]))
print("Revenue by service type:", m["revenue"]["by_service_type"])
print("Value buckets:", m["revenue"]["value_buckets"])
print("\nTOP ITEMS by revenue:")
for r in catalog[:12]: print("  {item:28} unit=${unit_price:<7} qty={total_qty:<5} rev=${revenue:<10} orders={orders}".format(**r))
print("\nOPS: completion={}%  complete={}  queued={}  issues={}  not_dispatched={}".format(
    m["operations"]["completion_rate"],m["operations"]["complete"],m["operations"]["queued"],m["operations"]["issues"],m["operations"]["not_dispatched"]))
print("Service mix:", m["operations"]["service_mix"])
print("\nDATES serv:", m["dates"]["serv_min"],"->",m["dates"]["serv_max"])
print("serv_daily:", m["dates"]["serv_daily"])
print("rev_daily:", {k:round(v) for k,v in m["dates"]["rev_daily"].items()})
print("\nDATA QUALITY:", json.dumps(dq, indent=2))
print("\nsaved ->", OUT)
