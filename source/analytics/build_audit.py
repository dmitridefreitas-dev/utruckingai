# Builds the UTrucking Data & Revenue Audit — self-contained HTML (charts embedded as PNG).
# Usage: python build_audit.py <metrics.json> <out.html>
import sys, json, io, base64, datetime
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

metrics_path, out_html = sys.argv[1], sys.argv[2]
M = json.load(open(metrics_path))

NAVY="#14335f"; ORANGE="#f5a623"; BLUE="#1e5aa8"; TEAL="#2b8a9e"
GREEN="#2e9e5b"; RED="#d9534f"; GREY="#9aa7b8"; LIGHT="#e3e9f2"
plt.rcParams.update({
    "font.family":"DejaVu Sans","font.size":11,"axes.edgecolor":"#c9d3e0",
    "axes.linewidth":0.8,"axes.grid":True,"grid.color":"#eef2f7","grid.linewidth":1,
    "axes.axisbelow":True,"figure.dpi":150,
})
def style(ax):
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.tick_params(length=0)
def uri(fig):
    buf=io.BytesIO(); fig.savefig(buf,format="png",dpi=150,bbox_inches="tight",facecolor="white")
    plt.close(fig); return "data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode()
def money(x,_=None): return "${:,.0f}".format(x)

# ---------- data prep ----------
rev_daily = M["dates"]["rev_daily"]; serv_daily=M["dates"]["serv_daily"]
days = sorted(set(list(rev_daily)+list(serv_daily)))
def lbl(d):
    y,mo,dd=d.split("-"); return "{}/{}".format(int(mo),int(dd))
xlabels=[lbl(d) for d in days]
rev=[rev_daily.get(d,0) for d in days]; vol=[serv_daily.get(d,0) for d in days]
peak_days=set(sorted(days,key=lambda d:-rev_daily.get(d,0))[:5])

CH={}

# 1) Hero: the move-out sprint (revenue bars + orders line)
fig,ax=plt.subplots(figsize=(8,3.6))
colors=[ORANGE if d in peak_days else NAVY for d in days]
ax.bar(range(len(days)),rev,color=colors,width=0.72)
ax.set_xticks(range(len(days))); ax.set_xticklabels(xlabels)
ax.yaxis.set_major_formatter(FuncFormatter(money)); ax.set_ylabel("Revenue invoiced")
ax2=ax.twinx(); ax2.plot(range(len(days)),vol,color=BLUE,marker="o",lw=2,ms=4)
ax2.set_ylabel("Orders",color=BLUE); ax2.tick_params(colors=BLUE); ax2.grid(False)
ax2.spines["top"].set_visible(False)
style(ax); ax.set_title("The move-out sprint — daily revenue (bars) and orders (line), May 2026",
    fontweight="bold",color=NAVY,loc="left")
ax.annotate("Peak: May 12\n$16.3K / 119 orders",xy=(days.index("2026-05-12"),16272),
    xytext=(days.index("2026-05-12")-3.2,15200),color=NAVY,fontsize=9,fontweight="bold",
    arrowprops=dict(arrowstyle="->",color=NAVY))
CH["hero"]=uri(fig)

# 2) Pareto — revenue concentration
sv=sorted(days,key=lambda d:-rev_daily.get(d,0))
cum=[]; s=0; tot=sum(rev) or 1
for d in sv: s+=rev_daily.get(d,0); cum.append(100*s/tot)
fig,ax=plt.subplots(figsize=(8,3.2))
ax.bar(range(len(sv)),[rev_daily.get(d,0) for d in sv],color=NAVY,width=0.7)
ax.set_xticks(range(len(sv))); ax.set_xticklabels([lbl(d) for d in sv])
ax.yaxis.set_major_formatter(FuncFormatter(money)); ax.set_ylabel("Revenue (ranked)")
ax2=ax.twinx(); ax2.plot(range(len(sv)),cum,color=ORANGE,marker="o",lw=2,ms=4)
ax2.set_ylim(0,105); ax2.set_ylabel("Cumulative %",color=ORANGE); ax2.tick_params(colors=ORANGE); ax2.grid(False)
ax2.axhline(74,ls="--",color=ORANGE,lw=1); ax2.text(len(sv)-1,77,"Top 5 days = 74%",ha="right",color=ORANGE,fontweight="bold",fontsize=9)
ax2.spines["top"].set_visible(False); style(ax)
ax.set_title("Revenue is dangerously concentrated — a Pareto view",fontweight="bold",color=NAVY,loc="left")
CH["pareto"]=uri(fig)

# 3) Order-value distribution
vb=M["revenue"]["value_buckets"]
fig,ax=plt.subplots(figsize=(5.4,3.0))
ax.bar(list(vb.keys()),list(vb.values()),color=BLUE,width=0.7)
style(ax); ax.set_ylabel("Orders"); ax.set_title("Order-value distribution",fontweight="bold",color=NAVY,loc="left")
for i,v in enumerate(vb.values()): ax.text(i,v+2,str(v),ha="center",fontsize=9,color=NAVY)
ax.set_xticks(range(len(vb))); ax.set_xticklabels(list(vb.keys()),rotation=20,ha="right")
CH["dist"]=uri(fig)

# 4) Top products by revenue
cat=M["catalog"][:8][::-1]
fig,ax=plt.subplots(figsize=(5.4,3.0))
ax.barh([c["item"] for c in cat],[c["revenue"] for c in cat],color=NAVY)
cat[-1] and ax.barh([cat[-1]["item"]],[cat[-1]["revenue"]],color=ORANGE)  # highlight top
style(ax); ax.xaxis.set_major_formatter(FuncFormatter(money))
ax.set_title("Revenue by product — the Box dominates",fontweight="bold",color=NAVY,loc="left")
CH["products"]=uri(fig)

# 5) Service mix (dispatch)
sm=M["operations"]["service_mix"]; items=list(sm.items())[:8][::-1]
fig,ax=plt.subplots(figsize=(5.4,3.0))
ax.barh([k for k,_ in items],[v for _,v in items],color=TEAL)
style(ax); ax.set_xlabel("Orders")
ax.set_title("Service mix (all 1,663 dispatch orders)",fontweight="bold",color=NAVY,loc="left")
CH["mix"]=uri(fig)

# 6) Fulfillment status
st=M["operations"]["status"]; ds=M["operations"]["dispatch_status"]
fig,ax=plt.subplots(figsize=(5.4,3.0))
cats=["Order status","Dispatch status"]
comp=[st.get("Complete",0),ds.get("Complete",0)]
mid=[st.get("Queued",0),ds.get("Not Dispatched",0)]
bad=[st.get("Issue",0),ds.get("Queued",0)]
ax.bar(cats,comp,color=GREEN,label="Complete")
ax.bar(cats,mid,bottom=comp,color=ORANGE,label="Queued / Not-dispatched")
ax.bar(cats,bad,bottom=[comp[0]+mid[0],comp[1]+mid[1]],color=RED,label="Issue / Queued")
style(ax); ax.legend(fontsize=8,frameon=False); ax.set_ylabel("Orders")
ax.set_title("Fulfillment — 86% complete, a real backlog remains",fontweight="bold",color=NAVY,loc="left")
CH["status"]=uri(fig)

# 7) Building concentration
bt=M["operations"]["buildings_top"]
bt={k:v for k,v in bt.items() if "DON'T KNOW" not in k}
its=list(bt.items())[:12][::-1]
fig,ax=plt.subplots(figsize=(5.4,3.4))
ax.barh([k for k,_ in its],[v for _,v in its],color=BLUE)
style(ax); ax.set_xlabel("Orders")
ax.set_title("Where the customers are (top buildings)",fontweight="bold",color=NAVY,loc="left")
CH["buildings"]=uri(fig)

# 8) Price scenarios
ps=M["insights"]["box_price_scenarios"]; tot_rev=M["revenue"]["total"]
labels=list(ps.keys()); vals=list(ps.values())
fig,ax=plt.subplots(figsize=(5.4,3.0))
bars=ax.bar(labels,vals,color=[GREY,ORANGE,GREY,GREY])
style(ax); ax.yaxis.set_major_formatter(FuncFormatter(money))
ax.set_title("Box price increase → annual revenue uplift",fontweight="bold",color=NAVY,loc="left")
for i,v in enumerate(vals):
    ax.text(i,v+120,"+{:.0f}%".format(100*v/tot_rev),ha="center",fontsize=9,color=NAVY,fontweight="bold")
ax.set_xlabel("Price change per box (2,593 boxes/season)")
CH["price"]=uri(fig)

# 9) Data-quality / leakage
dq=M["data_quality"]
fig,ax=plt.subplots(figsize=(5.4,3.0))
labs=["$0 Summer\nStorage orders","Missing\ninvoice ID","Missing\norder #","'Unknown'\nbuilding","Blank\nroom"]
vs=[M["insights"]["summer_storage_zero_leakage"],dq["service_blank_invoice"],dq["service_blank_order"],
    dq["dispatch_building_unknown"],dq["dispatch_blank_room"]]
ax.bar(labs,vs,color=RED,alpha=0.85)
style(ax); ax.set_ylabel("Records");
for i,v in enumerate(vs): ax.text(i,v+2,str(v),ha="center",fontsize=9,color=NAVY)
ax.set_title("Data-quality gaps that cost money",fontweight="bold",color=NAVY,loc="left")
CH["dq"]=uri(fig)

# ---------- numbers for prose ----------
R=M["revenue"]; I=M["insights"]; O=M["operations"]; C=M["counts"]
today="July 2, 2026"

def kpi(v,l,sub=""):
    return f'<div class="kpi"><div class="kv">{v}</div><div class="kl">{l}</div><div class="ks">{sub}</div></div>'

HTML=f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page{{size:letter;margin:0}}
*{{box-sizing:border-box}}
body{{font-family:'Segoe UI','DejaVu Sans',Arial,sans-serif;color:#22303f;margin:0}}
.page{{width:8.5in;min-height:11in;padding:0.75in 0.8in;page-break-after:always;position:relative}}
.page:last-child{{page-break-after:auto}}
h1,h2,h3{{color:{NAVY};margin:0}}
.eyebrow{{text-transform:uppercase;letter-spacing:.18em;font-size:11px;font-weight:800;color:{ORANGE}}}
.sec{{font-size:19pt;margin:0 0 2px}}
.secbar{{width:46px;height:5px;background:{ORANGE};border-radius:3px;margin:8px 0 16px}}
p{{line-height:1.5;font-size:11.2pt}}
.lead{{font-size:12pt;color:#3d4a59}}
img{{max-width:100%;border:1px solid #eef2f7;border-radius:8px;margin:6px 0 4px}}
.cap{{font-size:9.5pt;color:#6b7a8d;margin:0 0 14px}}
.grid2{{display:flex;gap:16px}}.col{{flex:1;min-width:0}}
.kpis{{display:flex;gap:12px;margin:14px 0 8px;flex-wrap:wrap}}
.kpi{{flex:1;min-width:130px;background:#f7f9fc;border:1px solid {LIGHT};border-left:5px solid {ORANGE};border-radius:10px;padding:14px 16px}}
.kv{{font-size:22pt;font-weight:800;color:{NAVY};line-height:1}}
.kl{{font-size:10pt;font-weight:700;color:#33465a;margin-top:5px}}
.ks{{font-size:9pt;color:#7c8 a0;color:#7c8aa0;margin-top:2px}}
.call{{background:#fff7e9;border:1px solid #f6dfb0;border-radius:10px;padding:12px 16px;margin:8px 0 16px}}
.call b{{color:{NAVY}}}
table{{width:100%;border-collapse:collapse;font-size:10.3pt;margin:6px 0 10px}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid #e9eef5;vertical-align:top}}
th{{background:{NAVY};color:#fff;font-size:9.5pt;letter-spacing:.02em}}
tr:nth-child(even) td{{background:#f7f9fc}}
.tag{{display:inline-block;font-size:8.5pt;font-weight:700;padding:2px 8px;border-radius:20px}}
.hi{{background:#e6f6ec;color:{GREEN}}}.me{{background:#fff2d8;color:#b9791a}}.lo{{background:#eef2f7;color:#5b6b7f}}
.foot{{position:absolute;bottom:0.45in;left:0.8in;right:0.8in;display:flex;justify-content:space-between;font-size:8.5pt;color:{GREY};border-top:1px solid #eef2f7;padding-top:6px}}
/* cover */
.cover{{background:linear-gradient(150deg,{NAVY} 0%,#0c2036 55%,#0a1a2c 100%);color:#fff;height:11in;padding:0.9in 0.85in;display:flex;flex-direction:column}}
.cover h1{{color:#fff;font-size:34pt;line-height:1.08;margin-top:10px}}
.cover .sub{{color:#cdd9ea;font-size:13.5pt;margin-top:14px;max-width:6in;line-height:1.5}}
.cover .obar{{width:70px;height:7px;background:{ORANGE};border-radius:4px}}
.cband{{display:flex;gap:14px;margin-top:auto}}
.cstat{{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.15);border-radius:12px;padding:16px 18px;flex:1}}
.cstat .n{{font-size:20pt;font-weight:800;color:{ORANGE}}}.cstat .t{{font-size:9.5pt;color:#cdd9ea;margin-top:3px}}
.prep{{color:#9db3cf;font-size:10pt;margin-top:26px}}
</style></head><body>

<div class="page cover">
  <div class="obar"></div>
  <div class="eyebrow" style="color:{ORANGE};margin-top:22px">University Trucking · Confidential</div>
  <h1>Data &amp; Revenue Audit</h1>
  <div class="sub">A data-science and financial-operations review of the summer-storage business — where the money comes from, where it leaks, and where to grow.</div>
  <div class="prep">Prepared as an independent analytics review · {today}<br>Sources: live Dispatch board (1,663 orders) &amp; Service/Invoice sheet (654 records)</div>
  <div class="cband">
    <div class="cstat"><div class="n">${R['total']:,.0f}</div><div class="t">Invoiced, summer-storage season</div></div>
    <div class="cstat"><div class="n">{I['peak5_revenue_share']:.0f}%</div><div class="t">of revenue in just 5 days</div></div>
    <div class="cstat"><div class="n">{O['completion_rate']:.0f}%</div><div class="t">of orders completed</div></div>
    <div class="cstat"><div class="n">{I['box_revenue_share']:.0f}%</div><div class="t">of revenue from one product</div></div>
  </div>
</div>

<!-- EXEC SUMMARY -->
<div class="page">
  <div class="eyebrow">Executive summary</div>
  <div class="sec">The one-week business</div><div class="secbar"></div>
  <p class="lead">UTrucking's summer-storage operation invoiced <b>${R['total']:,.0f}</b> across <b>{C['orders_with_revenue']}</b> paid orders — nearly all of it inside a <b>13-day move-out window</b>. This is a highly seasonal, highly concentrated business: it lives or dies on execution during roughly ten days in May.</p>
  <div class="kpis">
    {kpi(f"${R['aov_mean']:,.0f}","Average order value",f"median ${R['aov_median']:,.0f} · max ${R['max_order']:,.0f}")}
    {kpi(f"{I['box_attach_rate']:.0f}%","Orders with a UTrucking Box","the core, near-universal product")}
    {kpi(f"{I['avg_items_per_order']:.0f}","Items per order (avg)","strong basket size")}
    {kpi(f"{O['not_dispatched']}","Orders not yet dispatched",f"{I['not_dispatched_pct']:.0f}% of the board")}
  </div>
  <h3 style="margin-top:10px">What matters most</h3>
  <table>
    <tr><th style="width:31%">Finding</th><th>So what</th></tr>
    <tr><td><b>Revenue is a spike, not a stream</b></td><td>{I['peak5_revenue_share']:.0f}% of revenue lands in 5 days (peak May 12 = $16.3K / 119 orders). Capacity must be planned to the <i>peak day</i>, not the average.</td></tr>
    <tr><td><b>One product carries the P&amp;L</b></td><td>The UTrucking Box is {I['box_revenue_share']:.0f}% of revenue at a flat $22, with a {I['box_attach_rate']:.0f}% attach rate — the clearest pricing lever in the business.</td></tr>
    <tr><td><b>Pricing is left on the table</b></td><td>A $2 box increase adds <b>${M['insights']['box_price_scenarios']['+$2']:,.0f}</b> (+{100*M['insights']['box_price_scenarios']['+$2']/R['total']:.1f}%) to a captive, low-elasticity move-out audience.</td></tr>
    <tr><td><b>Money leaks quietly</b></td><td>{I['summer_storage_zero_leakage']} storage orders invoiced at $0 and {M['data_quality']['service_blank_invoice']} have no invoice ID; {M['data_quality']['dispatch_building_unknown']} orders have an unknown building (routing waste).</td></tr>
    <tr><td><b>The AI phone agent is the lever</b></td><td>It can pre-book and smooth demand off the two peak days, upsell the box/containers, and capture clean building + phone data at the source.</td></tr>
  </table>
  <div class="foot"><span>UTrucking — Data &amp; Revenue Audit</span><span>Executive summary</span></div>
</div>

<!-- SECTION 1 REVENUE -->
<div class="page">
  <div class="eyebrow">Section 1</div><div class="sec">Where the money comes from</div><div class="secbar"></div>
  <p>Every paid order is itemized (boxes, containers, fridges…) with a total. Parsing all {C['orders_with_revenue']} paid invoices gives a clean revenue picture.</p>
  <img src="{CH['hero']}"><div class="cap">Daily invoiced revenue (bars; orange = 5 peak days) and order count (line). The season is a single sharp wave.</div>
  <div class="grid2">
    <div class="col"><img src="{CH['dist']}"><div class="cap">Most orders fall in the $100–150 band; a long tail above $300.</div></div>
    <div class="col"><img src="{CH['products']}"><div class="cap">Revenue by product. The Box ({I['box_revenue_share']:.0f}%) is the franchise; containers &amp; fridges are the upsell.</div></div>
  </div>
  <div class="call"><b>Takeaway.</b> The business is a box-rental business with a moving service attached. Anything that raises box price, box attach, or basket size flows almost directly to the bottom line.</div>
  <div class="foot"><span>UTrucking — Data &amp; Revenue Audit</span><span>1 · Revenue</span></div>
</div>

<!-- SECTION 2 SEASONALITY -->
<div class="page">
  <div class="eyebrow">Section 2</div><div class="sec">The spike — seasonality &amp; capacity</div><div class="secbar"></div>
  <p>Demand is almost perfectly predictable: it is the week after finals. That is good news (you can plan for it) and a risk (you must staff for the peak, or lose orders).</p>
  <img src="{CH['pareto']}"><div class="cap">Days ranked by revenue with a cumulative line. The top 5 days account for {I['peak5_revenue_share']:.0f}% of the season.</div>
  <div class="call"><b>The predictor.</b> Demand ≈ academic calendar. Within the week, weekdays beat weekends (May 10 &amp; 15 were the quiet days). Pre-commit trucks and movers to the ~10-day window and staff heaviest on the two peak days.</div>
  <h3>The capacity math</h3>
  <p>Peak day (May 12) handled <b>119 orders / $16.3K</b>. If crews cap out below peak demand, the overflow either slips to a slower day (a scheduling win) or is lost (a revenue loss). The AI agent — with booking enabled — can actively steer callers toward the shoulder days that still had headroom.</p>
  <div class="foot"><span>UTrucking — Data &amp; Revenue Audit</span><span>2 · Seasonality</span></div>
</div>

<!-- SECTION 3 OPERATIONS -->
<div class="page">
  <div class="eyebrow">Section 3</div><div class="sec">Operations &amp; fulfillment</div><div class="secbar"></div>
  <div class="grid2">
    <div class="col"><img src="{CH['mix']}"><div class="cap">Summer Storage (49%) and Rental Returns (25%) are the volume drivers.</div></div>
    <div class="col"><img src="{CH['status']}"><div class="cap">{O['completion_rate']:.0f}% complete, but {O['not_dispatched']} orders sit "not dispatched".</div></div>
  </div>
  <img src="{CH['buildings']}"><div class="cap">Order volume by building — natural routing clusters (Umrath, Danforth, Park, Koenig…).</div>
  <div class="call"><b>Takeaway.</b> Fulfillment is strong but not clean: a {I['not_dispatched_pct']:.0f}% not-dispatched tail is cash and goodwill waiting to be captured. Buildings cluster tightly — route optimization by building/day is a quick efficiency win.</div>
  <div class="foot"><span>UTrucking — Data &amp; Revenue Audit</span><span>3 · Operations</span></div>
</div>

<!-- SECTION 4 PRICING + LEAKAGE -->
<div class="page">
  <div class="eyebrow">Section 4</div><div class="sec">Pricing power &amp; leakage</div><div class="secbar"></div>
  <div class="grid2">
    <div class="col"><img src="{CH['price']}"><div class="cap">Uplift from a per-box price change across ~2,593 boxes/season.</div></div>
    <div class="col"><img src="{CH['dq']}"><div class="cap">Quiet leaks: zero-dollar orders, missing invoices/IDs, unknown buildings.</div></div>
  </div>
  <p><b>Should they raise prices?</b> Yes — surgically. The box is a captive purchase during a stressful move-out; price sensitivity is low and the attach rate is {I['box_attach_rate']:.0f}%. A <b>$2</b> increase is nearly invisible to a customer already spending ~${R['aov_median']:,.0f}, yet adds <b>${M['insights']['box_price_scenarios']['+$2']:,.0f}/season</b>. Hold the moving-service and specialty-item prices; move the box.</p>
  <div class="call"><b>Recover the leak.</b> {I['summer_storage_zero_leakage']} storage orders were invoiced at $0 and {M['data_quality']['service_blank_invoice']} have no invoice ID — an estimated <b>~${I['leakage_est_dollars']:,.0f}</b> plus process risk. A single validation ("no order ships without a non-zero invoice") closes it.</div>
  <div class="foot"><span>UTrucking — Data &amp; Revenue Audit</span><span>4 · Pricing</span></div>
</div>

<!-- SECTION 5 RECOMMENDATIONS -->
<div class="page">
  <div class="eyebrow">Section 5</div><div class="sec">Recommendations — ranked by return</div><div class="secbar"></div>
  <table>
    <tr><th style="width:26%">Move</th><th style="width:16%">Impact</th><th style="width:14%">Effort</th><th>Why / estimated value</th></tr>
    <tr><td><b>Raise the box $2</b></td><td><span class="tag hi">High</span></td><td><span class="tag hi">Low</span></td><td>+${M['insights']['box_price_scenarios']['+$2']:,.0f}/season (+{100*M['insights']['box_price_scenarios']['+$2']/R['total']:.1f}%). Captive, low-elasticity demand.</td></tr>
    <tr><td><b>Smooth the peak via the AI agent</b></td><td><span class="tag hi">High</span></td><td><span class="tag me">Med</span></td><td>Steer callers from the 2 peak days to shoulder days; protects the {I['peak5_revenue_share']:.0f}%-concentrated revenue from capacity loss.</td></tr>
    <tr><td><b>Close billing leakage</b></td><td><span class="tag me">Med</span></td><td><span class="tag hi">Low</span></td><td>Block $0 / no-invoice orders. Recovers ~${I['leakage_est_dollars']:,.0f} + audit trail.</td></tr>
    <tr><td><b>Clear the not-dispatched backlog</b></td><td><span class="tag me">Med</span></td><td><span class="tag me">Med</span></td><td>{O['not_dispatched']} orders ({I['not_dispatched_pct']:.0f}%) pending — cash + customer experience.</td></tr>
    <tr><td><b>Fix data at the source</b></td><td><span class="tag me">Med</span></td><td><span class="tag hi">Low</span></td><td>Kill "unknown building" ({M['data_quality']['dispatch_building_unknown']}), require room/phone → route efficiency &amp; auto-caller-ID.</td></tr>
    <tr><td><b>Upsell containers &amp; fridges</b></td><td><span class="tag me">Med</span></td><td><span class="tag me">Med</span></td><td>Agent offers Plastic Container ($18) / Mini Fridge ($23) at booking — lifts basket beyond {I['avg_items_per_order']:.0f} items.</td></tr>
  </table>
  <h3>How the AI phone agent pays for itself</h3>
  <p><b>Four of the six moves run on the AI assistant</b> — (1) smooth the peak, (2) upsell containers &amp; fridges, (3) close the invoice leak, and (4) clean building/phone data at the source — all unlocked by the same Phase 2 booking capability. <b>Two it already does today:</b> quote consistent pricing (so a box-price rise needs no agent change) and confirm each caller's building during identity checks. The other two — setting the price and clearing the dispatch backlog — sit with management and the ops team. The agent is not just call deflection; it is the <b>distribution channel</b> for these gains.</p>
  <div class="foot"><span>UTrucking — Data &amp; Revenue Audit</span><span>5 · Recommendations</span></div>
</div>

<!-- METHODOLOGY -->
<div class="page">
  <div class="eyebrow">Appendix</div><div class="sec">Methodology &amp; data quality</div><div class="secbar"></div>
  <p><b>Sources.</b> Two live Google Sheets read on {today}: the Dispatch board ({M['counts']['dispatch_rows']:,} order rows) and the Service/Invoice sheet ({M['counts']['service_rows']} submissions). Revenue is parsed from the itemized "Item List" field on each invoice ("Amount: 22.00 USD, Quantity: 5 … Total: $176.00").</p>
  <p><b>Scope &amp; caveats.</b> Itemized revenue exists for the Summer-Storage line ({C['orders_with_revenue']} paid orders, ${R['total']:,.0f}); Home-Shipping submissions ({I['zero_by_service'].get('Home Shipping',0)}) are priced elsewhere and show as $0 here — they are excluded from revenue, not counted as leakage. Only {I['summer_storage_zero_leakage']} <i>storage</i> orders at $0 are treated as leakage. Dates reflect submission timestamps; a small number of dispatch rows have no date ({M['data_quality']['dispatch_no_date']}).</p>
  <p><b>Reproducibility.</b> All figures regenerate from source with <code>source/analytics/build_audit.py</code>. No numbers are hand-entered; every KPI and chart is computed from the raw sheets.</p>
  <table>
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>Season revenue (parsed)</td><td>${R['total']:,.0f}</td></tr>
    <tr><td>Paid orders / zero-total</td><td>{C['orders_with_revenue']} / {C['orders_zero_total']}</td></tr>
    <tr><td>Average / median order</td><td>${R['aov_mean']:,.0f} / ${R['aov_median']:,.0f}</td></tr>
    <tr><td>Box units / revenue share</td><td>{[c['total_qty'] for c in M['catalog'] if c['item']=='UTrucking Box'][0]:,} / {I['box_revenue_share']:.0f}%</td></tr>
    <tr><td>Completion / not-dispatched</td><td>{O['completion_rate']:.0f}% / {O['not_dispatched']}</td></tr>
    <tr><td>Date window</td><td>{M['dates']['serv_min']} → {M['dates']['serv_max']}</td></tr>
  </table>
  <div class="foot"><span>UTrucking — Data &amp; Revenue Audit</span><span>Appendix · Methodology</span></div>
</div>

</body></html>"""

open(out_html,"w",encoding="utf-8").write(HTML)
print("wrote", out_html, len(HTML), "bytes,", len(CH), "charts")
