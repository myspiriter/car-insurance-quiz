
import streamlit as st
import pandas as pd
import random, requests
from urllib.parse import quote

st.set_page_config(page_title="產險教育｜隨機抽車挑戰", page_icon="🚘", layout="wide")

st.markdown("""
<style>
.stApp {background: linear-gradient(145deg,#0b1220,#111827); color:white;}
.block-container {max-width:1100px; padding-top:1.5rem;}
.hero {padding:22px 28px;border:1px solid #334155;border-radius:22px;background:rgba(15,23,42,.85);margin-bottom:18px}
.price {font-size:2.1rem;font-weight:800}
.small {opacity:.72;font-size:.9rem}
div.stButton > button {width:100%;height:3.3rem;border-radius:14px;font-weight:800;font-size:1.05rem}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=86400)
def wiki_image(query):
    """從 Wikimedia Commons 尋找可公開瀏覽的車款圖片。"""
    try:
        api="https://commons.wikimedia.org/w/api.php"
        p={"action":"query","generator":"search","gsrsearch":query+" automobile",
           "gsrnamespace":6,"gsrlimit":8,"prop":"imageinfo","iiprop":"url","format":"json","origin":"*"}
        data=requests.get(api,params=p,timeout=8).json()
        pages=data.get("query",{}).get("pages",{})
        for x in pages.values():
            info=x.get("imageinfo",[{}])[0]
            u=info.get("url","")
            if u.lower().endswith((".jpg",".jpeg",".png",".webp")):
                return u
    except Exception:
        pass
    return None

df=pd.read_csv("cars.csv")
st.markdown('<div class="hero"><h1>🚘 產險教育｜隨機抽車挑戰</h1><div class="small">看車猜價格 → 揭曉 → 連結第三人責任財損與超額責任風險</div></div>', unsafe_allow_html=True)

c1,c2,c3=st.columns([1,1,1])
with c1:
    levels=st.multiselect("價格級別",sorted(df.level.unique()),default=list(sorted(df.level.unique())))
with c2:
    brands=st.multiselect("品牌（空白＝全部）",sorted(df.brand.unique()))
with c3:
    mode=st.selectbox("教學模式",["看圖猜車價","直接揭曉","產險情境題"])

pool=df[df.level.isin(levels)]
if brands: pool=pool[pool.brand.isin(brands)]
if pool.empty:
    st.warning("目前篩選沒有車款。")
    st.stop()

if "car_idx" not in st.session_state:
    st.session_state.car_idx=random.choice(pool.index.tolist())
if "reveal" not in st.session_state:
    st.session_state.reveal=(mode=="直接揭曉")

if st.button("🎲 隨機抽一台"):
    st.session_state.car_idx=random.choice(pool.index.tolist())
    st.session_state.reveal=(mode=="直接揭曉")

if st.session_state.car_idx not in pool.index:
    st.session_state.car_idx=random.choice(pool.index.tolist())

car=df.loc[st.session_state.car_idx]
img=wiki_image(f"{car.brand} {car.model}")

left,right=st.columns([1.35,1])
with left:
    if img:
        st.image(img,use_container_width=True)
        st.caption("圖片：Wikimedia Commons 搜尋結果；實際授權依原始圖片頁面為準。")
    else:
        st.info("目前找不到合適圖片，請再抽一次或在 cars.csv 加入自訂圖片欄位。")

with right:
    st.subheader("這台車值多少錢？")
    if mode!="看圖猜車價":
        st.markdown(f"### {car.brand} {car.model}")
    if not st.session_state.reveal and mode!="直接揭曉":
        st.markdown("## 💰 猜猜它的台灣參考新車價")
        if st.button("👀 揭曉答案"):
            st.session_state.reveal=True
            st.rerun()
    else:
        st.success("答案揭曉")
        st.markdown(f"### {car.brand} {car.model}")
        st.markdown(f'<div class="price">NT$ {car.price_twd_10k} 萬</div>',unsafe_allow_html=True)
        st.write(f"**級別：** {car.level}　｜　**車種：** {car['type']}")
        st.caption("價格為教育用參考新車價/價格區間；實際售價、年式、配備與保險重置價格請以原廠及保發中心最新資料為準。")

if mode=="產險情境題" and st.session_state.reveal:
    st.divider()
    st.subheader("💥 產險情境題")
    st.write(f"客戶駕車不慎造成 **{car.brand} {car.model}** 嚴重車損。若第三人責任險「財損」保額只有 **50萬元**，你會如何說明保障缺口？")
    with st.expander("查看教育重點"):
        st.markdown("""
- 第三人責任險的財損保額，是賠付他人財物損失的重要防線。
- 高價車的零件、鈑金、燈具、感測器與維修工資可能很高，單次事故未必只是「整台車價格」問題。
- 教育時可進一步討論：**第三人責任財損保額是否足夠、是否需要超額責任險，以及保額如何規劃。**
- 個案理賠仍須依事故責任、實際損害與保單條款認定。
        """)

st.divider()
st.caption("資料庫可直接編輯 cars.csv 擴充品牌與車款。Toyota 價格欄位已依 2026/10 查得之台灣官方售價整理；其他品牌第一版為教學用約略級距，正式授課前建議依原廠/保發中心最新資料更新。")
