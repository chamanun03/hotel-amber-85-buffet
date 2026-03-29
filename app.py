import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np

st.set_page_config(page_title="Hotel Amber 85 Buffet", layout="wide")

# ── Load data ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel('data/buffet_cleaned.xlsx')
    for col in ['queue_start_dt', 'queue_end_dt', 'meal_start_dt', 'meal_end_dt']:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

df = load_data()

BLUE   = '#4472C4'
ORANGE = '#ED7D31'
GRAY   = '#A6A6A6'
RED    = '#C00000'

def clean_ax(ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=10)

# ═════════════════════════════════════════════════════════════
# OVERVIEW
# ═════════════════════════════════════════════════════════════
st.title("Hotel Amber 85 — Breakfast Buffet Analysis")
st.markdown("---")
st.header("Overview")
st.markdown(
    "ข้อมูลจากบุฟเฟ่ต์อาหารเช้าของโรงแรม Amber 85 เก็บจากระบบคิวและการนั่งจริง "
    "รวม **5 วัน** (13–18 มีนาคม 2026) แบ่งลูกค้าเป็น 2 กลุ่ม: "
    "**Walk-in** (มาเฉพาะกินบุฟเฟ่ต์) และ **In-house** (แขกพักโรงแรม)"
)

seated = df[df['Guest_type'].notna()]
total_walkin  = int((df['Guest_type'] == 'Walk-in').sum())
total_inhouse = int((df['Guest_type'] == 'In-house').sum())
total_all     = total_walkin + total_inhouse

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Days of data",    f"{df['date'].nunique()} days")
c2.metric("Total groups",    f"{len(seated)}")
c3.metric("Total pax",       f"{int(seated['pax'].sum())}")
c4.metric("Walk-in groups",  f"{total_walkin}")
c5.metric("In-house groups", f"{total_inhouse}")

# stacked bar guest split
fig, ax = plt.subplots(figsize=(6, 0.9))
ax.barh([''], [total_walkin],  color=ORANGE, label='Walk-in')
ax.barh([''], [total_inhouse], color=BLUE,   label='In-house', left=total_walkin)
ax.text(total_walkin / 2, 0,
        f"Walk-in  {total_walkin/total_all*100:.0f}%",
        ha='center', va='center', color='white', fontsize=11, fontweight='bold')
ax.text(total_walkin + total_inhouse / 2, 0,
        f"In-house  {total_inhouse/total_all*100:.0f}%",
        ha='center', va='center', color='white', fontsize=11, fontweight='bold')
ax.axis('off')
st.pyplot(fig)
plt.close()

# ═════════════════════════════════════════════════════════════
# COMMENT 1
# ═════════════════════════════════════════════════════════════
st.markdown("---")
st.header("Task 1 statement analysis")
st.header("Comment 1 — In-house & Walk-in ต่างก็ไม่พอใจ")
st.markdown("> *\"In-house customers are unhappy that they have to wait for a table. Walk-in customers queue up for a long time and leave the queue because they don't want to wait any longer.\"*")
st.markdown(
    "In-house บ่นว่าต้องรอโต๊ะนาน ส่วน Walk-in รอคิวแล้วหนีไป — "
    "ตรวจสอบด้วย **เวลารอ** และ **walk-away rate**"
)

waited   = df[df['is_waited'] & df['wait_time_min'].notna()]
avg_wait = waited.groupby('Guest_type')['wait_time_min'].mean()

walkaways        = df[df['is_walkaway']]
wa_count         = walkaways['Guest_type'].value_counts()
total_waited_wk  = int((df['is_waited'] & (df['Guest_type'] == 'Walk-in')).sum())
total_waited_ih  = int((df['is_waited'] & (df['Guest_type'] == 'In-house')).sum())
wa_wk = int(wa_count.get('Walk-in', 0))
wa_ih = int(wa_count.get('In-house', 0))
rate_wk = wa_wk / total_waited_wk * 100 if total_waited_wk > 0 else 0
rate_ih = wa_ih / total_waited_ih * 100 if total_waited_ih > 0 else 0

c1, c2 = st.columns(2)

with c1:
    st.subheader("Avg Wait Time (min)")
    types = ['Walk-in', 'In-house']
    vals  = [avg_wait.get(t, 0) for t in types]
    fig, ax = plt.subplots(figsize=(4, 3))
    bars = ax.bar(types, vals, color=[ORANGE, BLUE], width=0.4)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
                f'{v:.0f} min', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.set_ylabel('Minutes')
    ax.set_ylim(0, max(vals) * 1.35)
    clean_ax(ax)
    st.pyplot(fig)
    plt.close()
    st.caption(
        f"In-house รอเฉลี่ย **{avg_wait.get('In-house',0):.0f} นาที** "
        f"| Walk-in รอเฉลี่ย **{avg_wait.get('Walk-in',0):.0f} นาที**"
    )

with c2:
    st.subheader("Walk-away Rate")
    x      = np.arange(2)
    labels = ['Walk-in', 'In-house']
    totals = [total_waited_wk, total_waited_ih]
    was    = [wa_wk, wa_ih]
    rates  = [rate_wk, rate_ih]

    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(x - 0.2, totals, width=0.35, color=GRAY,  label='Waited in queue')
    ax.bar(x + 0.2, was,    width=0.35, color=RED,   label='Walked away')
    for i, (t, w, r) in enumerate(zip(totals, was, rates)):
        ax.text(i - 0.2, t + 0.1, str(t), ha='center', va='bottom', fontsize=10)
        ax.text(i + 0.2, w + 0.1, f'{w}\n({r:.0f}%)',
                ha='center', va='bottom', fontsize=10, fontweight='bold', color=RED)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel('Groups')
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.legend(fontsize=9)
    clean_ax(ax)
    st.pyplot(fig)
    plt.close()
    st.caption(
        f"Walk-in หนีคิว **{wa_wk} กลุ่ม ({rate_wk:.0f}%)** "
        f"| In-house หนีคิว **{wa_ih} กลุ่ม ({rate_ih:.0f}%)**"
    )

st.info("สรุป: คำพูดนี้ถูกต้อง — ทั้งสองกลุ่มได้รับผลกระทบจากปัญหาการรอจริง")

# ═════════════════════════════════════════════════════════════
# COMMENT 2
# ═════════════════════════════════════════════════════════════
st.markdown("---")
st.header("Comment 2 — ยุ่งทุกวัน หรือแค่ช่วง Weekend?")
st.markdown("> *\"We are very busy every day of the week. If it's going to be this busy every week I think it's impossible to sustain this business.\"*")
st.markdown(
    "เทียบจำนวน group ต่อวัน โดยแยกสีระหว่างวันธรรมดา (น้ำเงิน) และ weekend (ส้ม)"
)

daily = (seated
         .groupby(['date', 'day_of_week'])
         .agg(groups=('service_no.', 'count'), pax=('pax', 'sum'))
         .reset_index()
         .sort_values('date'))
daily['label']    = daily['day_of_week'].str[:3] + '\n' + daily['date'].str[5:]
daily['is_wkend'] = daily['day_of_week'].isin(['Friday', 'Saturday', 'Sunday'])
bar_colors        = [ORANGE if w else BLUE for w in daily['is_wkend']]

c1, c2 = st.columns(2)

with c1:
    st.subheader("Groups per Day")
    fig, ax = plt.subplots(figsize=(5, 3.2))
    bars = ax.bar(daily['label'], daily['groups'], color=bar_colors)
    ax.axhline(daily['groups'].mean(), color='black', linewidth=1.2,
               linestyle='--')
    ax.text(len(daily) - 0.5, daily['groups'].mean() + 0.5,
            f"avg {daily['groups'].mean():.0f}", fontsize=9, color='black')
    for bar, v in zip(bars, daily['groups']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                str(int(v)), ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.set_ylabel('Groups')
    ax.set_ylim(0, daily['groups'].max() * 1.3)
    legend_els = [mpatches.Patch(color=ORANGE, label='Weekend'),
                  mpatches.Patch(color=BLUE,   label='Weekday')]
    ax.legend(handles=legend_els, fontsize=9)
    clean_ax(ax)
    st.pyplot(fig)
    plt.close()

with c2:
    st.subheader("Total Pax per Day")
    fig, ax = plt.subplots(figsize=(5, 3.2))
    bars = ax.bar(daily['label'], daily['pax'], color=bar_colors)
    ax.axhline(daily['pax'].mean(), color='black', linewidth=1.2, linestyle='--')
    ax.text(len(daily) - 0.5, daily['pax'].mean() + 0.5,
            f"avg {daily['pax'].mean():.0f}", fontsize=9, color='black')
    for bar, v in zip(bars, daily['pax']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                str(int(v)), ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.set_ylabel('Pax')
    ax.set_ylim(0, daily['pax'].max() * 1.3)
    ax.legend(handles=legend_els, fontsize=9)
    clean_ax(ax)
    st.pyplot(fig)
    plt.close()

wkday = daily[~daily['is_wkend']]
wkend = daily[daily['is_wkend']]
st.caption(
    f"Weekday avg: **{wkday['groups'].mean():.0f} groups / {wkday['pax'].mean():.0f} pax** "
    f"| Weekend avg: **{wkend['groups'].mean():.0f} groups / {wkend['pax'].mean():.0f} pax**"
)
st.info("สรุป: ยุ่งทุกวันจริง ไม่ใช่แค่ weekend — วันธรรมดาก็มีลูกค้าใกล้เคียงกัน")

# ═════════════════════════════════════════════════════════════
# COMMENT 3
# ═════════════════════════════════════════════════════════════
st.markdown("---")
st.header("Comment 3 — Walk-in นั่งนานกว่า In-house จริงไหม?")
st.markdown("> *\"Walk-in customers sit the whole day. It's very difficult to find seats for in-house customers. We don't have enough tables.\"*")
st.markdown(
    "เปรียบเทียบเวลาที่ใช้บนโต๊ะ (meal duration) ระหว่าง Walk-in กับ In-house "
    "ด้วย box plot และ histogram"
)

dur    = df[df['meal_duration_min'].notna() & df['Guest_type'].notna()].copy()
wk_dur = dur[dur['Guest_type'] == 'Walk-in']['meal_duration_min']
ih_dur = dur[dur['Guest_type'] == 'In-house']['meal_duration_min']

c1, c2 = st.columns(2)

with c1:
    st.subheader("Meal Duration — Box Plot")
    fig, ax = plt.subplots(figsize=(4, 3.5))
    bp = ax.boxplot([wk_dur.dropna(), ih_dur.dropna()],
                    labels=['Walk-in', 'In-house'],
                    patch_artist=True,
                    medianprops=dict(color='black', linewidth=2),
                    whiskerprops=dict(linewidth=1.2),
                    capprops=dict(linewidth=1.2))
    bp['boxes'][0].set_facecolor(ORANGE)
    bp['boxes'][1].set_facecolor(BLUE)
    for box in bp['boxes']:
        box.set_alpha(0.7)
    ax.set_ylabel('Minutes')
    ax.yaxis.set_major_locator(mticker.MultipleLocator(30))
    clean_ax(ax)
    st.pyplot(fig)
    plt.close()
    st.caption(
        f"Walk-in median: **{wk_dur.median():.0f} min** "
        f"| In-house median: **{ih_dur.median():.0f} min**"
    )

with c2:
    st.subheader("Meal Duration — Distribution")
    fig, ax = plt.subplots(figsize=(4, 3.5))
    ax.hist(wk_dur, bins=20, color=ORANGE, alpha=0.6, label='Walk-in',  edgecolor='white')
    ax.hist(ih_dur, bins=20, color=BLUE,   alpha=0.6, label='In-house', edgecolor='white')
    ax.axvline(wk_dur.mean(), color=ORANGE, linewidth=2, linestyle='--',
               label=f'Walk-in avg {wk_dur.mean():.0f}m')
    ax.axvline(ih_dur.mean(), color=BLUE,   linewidth=2, linestyle='--',
               label=f'In-house avg {ih_dur.mean():.0f}m')
    ax.set_xlabel('Minutes')
    ax.set_ylabel('Groups')
    ax.legend(fontsize=8)
    clean_ax(ax)
    st.pyplot(fig)
    plt.close()

# long sitters
long_cut = 120
long_df  = dur[dur['meal_duration_min'] > long_cut]
long_by  = long_df['Guest_type'].value_counts().reset_index()
long_by.columns = ['Guest Type', 'Groups > 2hr']
long_by['% of their group'] = long_by.apply(
    lambda r: f"{r['Groups > 2hr'] / len(dur[dur['Guest_type'] == r['Guest Type']]) * 100:.1f}%",
    axis=1
)
st.subheader("กลุ่มที่นั่งนานกว่า 2 ชั่วโมง (>120 min)")
st.dataframe(long_by, use_container_width=False, hide_index=True)

diff = wk_dur.mean() - ih_dur.mean()
if diff > 5:
    st.info(
        f"สรุป: Walk-in นั่งเฉลี่ย {wk_dur.mean():.0f} นาที vs In-house {ih_dur.mean():.0f} นาที "
        f"— ต่างกัน {diff:.0f} นาที คำพูดนี้ถูกต้อง"
    )
else:
    st.warning(
        f"สรุป: Walk-in นั่งเฉลี่ย {wk_dur.mean():.0f} นาที vs In-house {ih_dur.mean():.0f} นาที "
        f"— ต่างกันแค่ {abs(diff):.0f} นาที ไม่ชัดเจนเท่าที่คิด"
    )
# ═════════════════════════════════════════════════════════════
# TASK 2 — หักล้าง 3 มาตรการ
# ═════════════════════════════════════════════════════════════
st.markdown("---")
st.header("Task 2 — ทำไมแต่ละมาตรการจะไม่ได้ผล")
st.markdown(
    "ฝ่ายบริหารเสนอ 3 มาตรการเพื่อแก้ปัญหา — "
    "วิเคราะห์จากข้อมูลจริงว่าแต่ละมาตรการจะไม่แก้ปัญหาได้จริง"
)

# ─────────────────────────────────────────────────────────────
# ACTION 1 — ลดเวลานั่ง
# ─────────────────────────────────────────────────────────────
st.subheader("Action 1 — ลดเวลานั่งจาก 5 ชั่วโมง")
st.markdown("> *\"Reduce seating time (5 hours to less)\"*")
st.markdown(
    "ถ้าคนส่วนใหญ่นั่งไม่ถึง 5 ชั่วโมงอยู่แล้ว การลด time limit ไม่ได้ไล่ใครออก "
    "และไม่ได้เพิ่ม table turnover จริง"
)

dur = df[df['meal_duration_min'].notna() & df['Guest_type'].notna()].copy()
total_dur = len(dur)

cutoffs   = [60, 90, 120, 150, 180, 240, 300]
over_pct  = [len(dur[dur['meal_duration_min'] > c]) / total_dur * 100 for c in cutoffs]
labels_c  = [f'{c//60}h' if c % 60 == 0 else f'{c}min' for c in cutoffs]

c1, c2 = st.columns(2)

with c1:
    st.subheader("Meal Duration Distribution")
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.hist(dur['meal_duration_min'], bins=30, color=BLUE, edgecolor='white', alpha=0.8)
    for cut, col, ls in [(60, GRAY, ':'), (120, ORANGE, '--'), (300, RED, '-')]:
        n   = len(dur[dur['meal_duration_min'] > cut])
        pct = n / total_dur * 100
        ax.axvline(cut, color=col, linewidth=1.8, linestyle=ls,
                   label=f'>{cut}min: {n} groups ({pct:.0f}%)')
    ax.set_xlabel('Minutes')
    ax.set_ylabel('Groups')
    ax.legend(fontsize=8)
    clean_ax(ax)
    st.pyplot(fig)
    plt.close()

with c2:
    st.subheader("% ที่นั่งเกิน time limit แต่ละระดับ")
    fig, ax = plt.subplots(figsize=(5, 3.5))
    bar_cols = [RED if p < 10 else ORANGE if p < 30 else BLUE for p in over_pct]
    bars = ax.bar(labels_c, over_pct, color=bar_cols)
    for bar, v in zip(bars, over_pct):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
                f'{v:.0f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_ylabel('% of all groups')
    ax.set_ylim(0, max(over_pct) * 1.3)
    ax.set_xlabel('Time limit')
    clean_ax(ax)
    st.pyplot(fig)
    plt.close()

pct_over2h = len(dur[dur['meal_duration_min'] > 120]) / total_dur * 100
pct_over3h = len(dur[dur['meal_duration_min'] > 180]) / total_dur * 100
st.caption(
    f"นั่งนานกว่า 2 ชั่วโมง: **{pct_over2h:.0f}%** | "
    f"นานกว่า 3 ชั่วโมง: **{pct_over3h:.0f}%** | "
    f"ส่วนใหญ่นั่ง **{dur['meal_duration_min'].median():.0f} นาที (median)**"
)
st.info(
    f"สรุป: มาตรการนี้ไม่ได้ผล — "
    f"กว่า {100-pct_over2h:.0f}% ของลูกค้านั่งไม่ถึง 2 ชั่วโมงอยู่แล้ว "
    f"การลด time limit ไม่ได้เพิ่ม table turnover จริง ปัญหาคือโต๊ะไม่พอ ไม่ใช่คนนั่งนานเกินไป"
)

# ─────────────────────────────────────────────────────────────
# ACTION 2 — ขึ้นราคาเป็น 259
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Action 2 — ขึ้นราคาทุกวันเป็น 259 บาท")
st.markdown("> *\"Increase price everyday to 259\"*")
st.markdown(
    "ราคาปัจจุบัน weekday 159 บาท weekend 199 บาท — "
    "วันหยุดแพงกว่าแต่คนก็มาเยอะกว่า แสดงว่าราคาไม่ใช่ตัวขับไล่ความต้องการ"
)

seated2 = df[df['Guest_type'].notna()].copy()
daily2  = (seated2
           .groupby(['date', 'day_of_week'])
           .agg(groups=('service_no.', 'count'), pax=('pax', 'sum'))
           .reset_index()
           .sort_values('date'))
daily2['is_wkend'] = daily2['day_of_week'].isin(['Friday', 'Saturday', 'Sunday'])
daily2['price']    = daily2['is_wkend'].map({True: 199, False: 159})
daily2['label']    = daily2['day_of_week'].str[:3] + '\n' + daily2['date'].str[5:]
bar_cols2          = [ORANGE if w else BLUE for w in daily2['is_wkend']]

c1, c2 = st.columns(2)

with c1:
    st.subheader("Groups per Day — แยกราคา")
    fig, ax = plt.subplots(figsize=(5, 3.5))
    bars = ax.bar(daily2['label'], daily2['groups'], color=bar_cols2)
    for bar, v, p in zip(bars, daily2['groups'], daily2['price']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{int(v)}\n(฿{p})', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.set_ylabel('Groups')
    ax.set_ylim(0, daily2['groups'].max() * 1.4)
    legend_els = [mpatches.Patch(color=ORANGE, label='Weekend ฿199'),
                  mpatches.Patch(color=BLUE,   label='Weekday ฿159')]
    ax.legend(handles=legend_els, fontsize=9)
    clean_ax(ax)
    st.pyplot(fig)
    plt.close()

with c2:
    st.subheader("Avg Groups — ฿159 vs ฿199")
    price_avg = daily2.groupby('price')['groups'].mean().reset_index()
    fig, ax   = plt.subplots(figsize=(5, 3.5))
    cols_p    = [BLUE, ORANGE]
    bars = ax.bar([f'฿{int(p)}' for p in price_avg['price']],
                  price_avg['groups'], color=cols_p, width=0.4)
    for bar, v in zip(bars, price_avg['groups']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                f'{v:.0f} groups', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.set_ylabel('Avg groups per day')
    ax.set_ylim(0, price_avg['groups'].max() * 1.35)
    clean_ax(ax)
    st.pyplot(fig)
    plt.close()

avg_159 = daily2[~daily2['is_wkend']]['groups'].mean()
avg_199 = daily2[daily2['is_wkend']]['groups'].mean()
st.caption(
    f"ราคา ฿159 (weekday) avg **{avg_159:.0f} groups/day** | "
    f"ราคา ฿199 (weekend) avg **{avg_199:.0f} groups/day**"
)
st.info(
    f"สรุป: มาตรการนี้ไม่ได้ผล — "
    f"weekend ราคา ฿199 แต่มีลูกค้าเฉลี่ย {avg_199:.0f} groups ต่อวัน "
    f"สูงกว่า weekday ฿159 ที่ {avg_159:.0f} groups "
    f"แสดงว่าลูกค้าไม่ได้ตัดสินใจจากราคา การขึ้นราคาเป็น ฿259 ไม่ลด demand "
    f"แต่จะสร้างความไม่พอใจโดยเปล่าประโยชน์"
)

# ─────────────────────────────────────────────────────────────
# ACTION 3 — ให้ In-house ข้ามคิว
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Action 3 — ให้ In-house ข้ามคิว")
st.markdown("> *\"Queue skipping for in-house guests\"*")
st.markdown(
    "ถ้า In-house ส่วนใหญ่ไม่ได้รอคิวอยู่แล้ว การข้ามคิวไม่ได้ช่วยอะไร "
    "ปัญหาจริงคือโต๊ะเต็ม ไม่ใช่ลำดับคิว"
)

ih = df[df['Guest_type'] == 'In-house'].copy()
ih_waited = int(ih['is_waited'].sum())
ih_direct = int(ih['is_direct_seat'].sum())
ih_total  = ih_waited + ih_direct

wk = df[df['Guest_type'] == 'Walk-in'].copy()
wk_waited = int(wk['is_waited'].sum())
wk_direct = int(wk['is_direct_seat'].sum())

c1, c2 = st.columns(2)

with c1:
    st.subheader("In-house — รอคิว vs นั่งได้เลย")
    fig, ax = plt.subplots(figsize=(4, 3.5))
    vals_ih = [ih_direct, ih_waited]
    labs_ih = [f'Direct seat\n{ih_direct} ({ih_direct/ih_total*100:.0f}%)',
               f'Waited\n{ih_waited} ({ih_waited/ih_total*100:.0f}%)']
    wedge_cols = [BLUE, ORANGE]
    ax.pie(vals_ih, labels=labs_ih, colors=wedge_cols,
           autopct='', startangle=90,
           wedgeprops=dict(edgecolor='white', linewidth=2))
    ax.set_title('In-house seating pattern', fontsize=11)
    st.pyplot(fig)
    plt.close()
    st.caption(
        f"In-house **{ih_direct/ih_total*100:.0f}%** นั่งได้เลยโดยไม่ต้องรอคิว "
        f"มีแค่ **{ih_waited/ih_total*100:.0f}%** ที่รอคิวจริง"
    )

with c2:
    st.subheader("Walk-in vs In-house — Queue Pattern")
    fig, ax = plt.subplots(figsize=(4, 3.5))
    x       = np.arange(2)
    labels3 = ['Walk-in', 'In-house']
    directv = [wk_direct, ih_direct]
    waitedv = [wk_waited, ih_waited]
    ax.bar(x, directv, color=BLUE,   label='Direct seat', width=0.5)
    ax.bar(x, waitedv, color=ORANGE, label='Waited',      width=0.5, bottom=directv)
    for i, (d, w) in enumerate(zip(directv, waitedv)):
        total = d + w
        ax.text(i, total + 0.5, str(total), ha='center', va='bottom', fontsize=10)
        ax.text(i, d/2,       f'{d}', ha='center', va='center', color='white', fontsize=9, fontweight='bold')
        ax.text(i, d + w/2,   f'{w}', ha='center', va='center', color='white', fontsize=9, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels3)
    ax.set_ylabel('Groups')
    ax.legend(fontsize=9)
    clean_ax(ax)
    st.pyplot(fig)
    plt.close()
    st.caption(
        f"Walk-in รอคิว **{wk_waited} กลุ่ม** | "
        f"In-house รอคิวแค่ **{ih_waited} กลุ่ม** จาก {ih_total} กลุ่มทั้งหมด"
    )

st.info(
    f"สรุป: มาตรการนี้ไม่ได้ผล — "
    f"In-house กว่า {ih_direct/ih_total*100:.0f}% นั่งได้เลยโดยไม่รอคิวอยู่แล้ว "
    f"การให้ข้ามคิวช่วยได้แค่ {ih_waited} กลุ่มเท่านั้น "
    f"ปัญหาจริงคือโต๊ะเต็มตลอด ไม่ใช่ลำดับคิว"
)

# ═════════════════════════════════════════════════════════════
# TASK 3 — Action 1: 90-Minute Limit (Extra)
# ═════════════════════════════════════════════════════════════
st.markdown("---")
st.header("Task 3 — มาตรการที่ดีที่สุด: กำหนด 90 นาที")
st.markdown("> *\"Reduce seating time — adjusted to 90-minute soft limit\"*")
st.markdown(
    "จาก Task 2 ถ้าปรับเป็น **90 นาที** จะกระทบกี่คน และช่วยเพิ่ม turnover ได้จริงไหม"
)

LIMIT = 90

dur3   = df[df['meal_duration_min'].notna() & df['Guest_type'].notna()].copy()
total3 = len(dur3)

over_limit  = dur3[dur3['meal_duration_min'] > LIMIT]
under_limit = dur3[dur3['meal_duration_min'] <= LIMIT]
n_over      = len(over_limit)
n_under     = len(under_limit)
pct_over    = n_over  / total3 * 100
pct_under   = n_under / total3 * 100

# over by guest type
over_by_type = over_limit['Guest_type'].value_counts()

# ── KPI ──────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("กลุ่มที่จะโดน limit",    f"{n_over} groups")
c2.metric("% ที่โดน limit",         f"{pct_over:.0f}%")
c3.metric("กลุ่มที่ไม่กระทบ",       f"{n_under} groups")
c4.metric("% ที่ไม่กระทบ",          f"{pct_under:.0f}%")

c1, c2 = st.columns(2)

# Chart 3.1 — distribution with 90-min line
with c1:
    st.subheader("Meal Duration — ก่อน vs หลัง Limit")
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.hist(under_limit['meal_duration_min'], bins=25, color=BLUE,
            alpha=0.8, label=f'Under {LIMIT}min ({pct_under:.0f}%)', edgecolor='white')
    ax.hist(over_limit['meal_duration_min'],  bins=15, color=RED,
            alpha=0.8, label=f'Over {LIMIT}min ({pct_over:.0f}%)',  edgecolor='white')
    ax.axvline(LIMIT, color='black', linewidth=2, linestyle='--', label=f'{LIMIT}-min limit')
    ax.set_xlabel('Minutes')
    ax.set_ylabel('Groups')
    ax.legend(fontsize=8)
    clean_ax(ax)
    st.pyplot(fig)
    plt.close()
    st.caption(
        f"กลุ่มที่นั่งเกิน 90 นาที: Walk-in **{over_by_type.get('Walk-in',0)} กลุ่ม** "
        f"| In-house **{over_by_type.get('In-house',0)} กลุ่ม**"
    )

# Chart 3.2 — turnover simulation
with c2:
    st.subheader("Table Turnover — ก่อน vs หลัง Limit")

    # avg meal duration before and after
    avg_before = dur3['meal_duration_min'].mean()
    # after: cap over-limit groups at 90 min
    dur3['meal_capped'] = dur3['meal_duration_min'].clip(upper=LIMIT)
    avg_after  = dur3['meal_capped'].mean()

    # turnover = how many seatings per table in a 5-hr window
    window_min  = 300  # 5 hours
    turns_before = window_min / avg_before
    turns_after  = window_min / avg_after
    improvement  = (turns_after - turns_before) / turns_before * 100

    fig, ax = plt.subplots(figsize=(5, 3.5))
    scenarios = ['Before\n(no limit)', f'After\n({LIMIT}-min limit)']
    turns     = [turns_before, turns_after]
    cols_t    = [GRAY, BLUE]
    bars = ax.bar(scenarios, turns, color=cols_t, width=0.4)
    for bar, v in zip(bars, turns):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{v:.1f}x', ha='center', va='bottom', fontsize=13, fontweight='bold')
    ax.set_ylabel('Avg seatings per table (5-hr window)')
    ax.set_ylim(0, max(turns) * 1.3)
    ax.annotate('', xy=(1, turns_after), xytext=(0, turns_before),
                arrowprops=dict(arrowstyle='->', color=RED, lw=2))
    ax.text(0.5, (turns_before + turns_after)/2 + 0.05,
            f'+{improvement:.0f}%', ha='center', color=RED,
            fontsize=12, fontweight='bold')
    clean_ax(ax)
    st.pyplot(fig)
    plt.close()
    st.caption(
        f"avg meal ลดจาก **{avg_before:.0f} นาที → {avg_after:.0f} นาที** "
        f"| turnover เพิ่มขึ้น **{improvement:.0f}%**"
    )

# ── Extra groups gained per day ───────────────────────────────
# estimate: time freed per day by capping over-limit groups
time_freed_per_day = over_limit.groupby('date').apply(
    lambda x: (x['meal_duration_min'] - LIMIT).clip(lower=0).sum()
).mean()

# assume avg table freed can seat 1 group at avg 61 min
groups_gained = time_freed_per_day / avg_after
avg_pax_per_group = dur3['pax'].mean()

st.subheader("ประมาณการลูกค้าที่รองรับเพิ่มได้ต่อวัน")
c1, c2, c3 = st.columns(3)
c1.metric("เวลาที่ได้คืนต่อวัน (avg)",     f"{time_freed_per_day:.0f} min")
c2.metric("กลุ่มที่รองรับเพิ่มได้",         f"~{groups_gained:.0f} groups")
c3.metric("PAX ที่รองรับเพิ่มได้",           f"~{groups_gained * avg_pax_per_group:.0f} pax")

# ── Why best ─────────────────────────────────────────────────
st.markdown("---")
st.subheader("ทำไม 90-Minute Limit ถึงเป็นตัวเลือกที่ดีที่สุด")

st.markdown(f"""
**เปรียบเทียบกับ 3 มาตรการเดิม**

| มาตรการ | ปัญหา | ผลลัพธ์จริง |
|---|---|---|
| ขึ้นราคา 259 | คนมาเพราะชอบ ไม่ใช่เพราะราคาถูก | ลด demand โดยไม่จำเป็น |
| Queue skip | In-house {ih_direct/ih_total*100:.0f}% นั่งได้เลยอยู่แล้ว | แก้ผิดจุด |
| **90-min limit** | **ตรงจุด: เพิ่ม turnover จากต้นเหตุ** | **+{improvement:.0f}% turnover** |
""")

st.markdown(f"""
**เหตุผลที่เลือก 90 นาที**
- Median ของทุกกลุ่มอยู่ที่ **{dur3['meal_duration_min'].median():.0f} นาที** — 90 นาทีให้เวลาเกินพอสำหรับคนส่วนใหญ่
- กระทบแค่ **{pct_over:.0f}%** ของลูกค้าทั้งหมด ไม่ได้รบกวนประสบการณ์คนส่วนใหญ่
- เพิ่มความสามารถรองรับได้ **~{groups_gained:.0f} กลุ่ม/วัน** โดยไม่ต้องลงทุนเพิ่ม
- แนะนำทำแบบแจ้งเตือนล่วงหน้า 15 นาที แทนการบังคับออก 
  เพื่อรักษาประสบการณ์ที่ดีของลูกค้า
""")

st.success(
    f"สรุป: กำหนด 90-minute limit คือมาตรการที่ดีที่สุดจากข้อมูลที่มี — "
    f"กระทบลูกค้าเพียง {pct_over:.0f}% แต่เพิ่ม turnover ได้ {improvement:.0f}% "
    f"และรองรับลูกค้าเพิ่มได้ ~{groups_gained:.0f} กลุ่มต่อวัน โดยไม่ต้องขึ้นราคาหรือเพิ่มโต๊ะ"
)

st.markdown("---")
st.caption("Data: 2026 Data Test1 Final - Busy Buffet Dataset")