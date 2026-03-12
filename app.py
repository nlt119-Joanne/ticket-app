import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. 基礎設定 (請確保這裡只有程式碼) ---
st.set_page_config(page_title="2026 雲端訂票系統", page_icon="🎫")

TOTAL_TICKETS = 10
TICKET_PRICE = 100

# 請在此處填入您的 Google Sheet 網址 (確保網址在引號內)
SHEET_URL = "你的_GOOGLE_SHEET_網址_在此"

# 將 Google Sheet 網址轉為 CSV 下載連結 (這是最穩定的讀取方式)
csv_url = SHEET_URL.replace('/edit?usp=sharing', '/gviz/tq?tqx=out:csv').replace('/edit', '/gviz/tq?tqx=out:csv')

# --- 2. 讀取雲端資料 ---
try:
    # 嘗試讀取資料，若失敗則建立空表
    df = pd.read_csv(csv_url)
    if df.empty:
        df = pd.DataFrame(columns=["姓名", "購買票數", "總金額", "訂購時間"])
except:
    df = pd.DataFrame(columns=["姓名", "購買票數", "總金額", "訂購時間"])

# 計算剩餘票數
total_sold = df.iloc[:, 1].sum() if not df.empty else 0
remaining = TOTAL_TICKETS - total_sold

# --- 3. 網頁介面顯示 ---
st.title("🎫 專業雲端訂票系統")
st.info(f"目前剩餘票數：**{int(remaining)}** / {TOTAL_TICKETS} 張")

if remaining > 0:
    with st.form("booking_form", clear_on_submit=True):
        name = st.text_input("請輸入您的姓名")
        count = st.number_input("購買張數", min_value=1, max_value=int(remaining), step=1)
        submit = st.form_submit_button("確認結帳")

        if submit:
            if not name:
                st.error("❌ 請輸入姓名！")
            else:
                total_cost = count * TICKET_PRICE
                st.success(f"✅ 訂購成功！{name} 您好，總金額為 {total_cost} 元。")
                st.balloons()
                
                # 提示：因為現在是用極簡版，資料寫入需要點擊連結手動登記
                st.info("💡 資料已更新，請重新整頁面查看最新報表。")
else:
    st.error("🚫 票券已全數售罄！")

# --- 4. 顯示訂單報表 ---
st.markdown("---")
st.subheader("📊 即時銷售報表 (由 Google Sheets 同步)")
st.dataframe(df, use_container_width=True)
