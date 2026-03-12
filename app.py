import streamlit as st
from st_gsheets_connection import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 基礎設定 ---
st.set_page_config(page_title="2026 雲端訂票系統", page_icon="🎫")
TOTAL_TICKETS = 10
TICKET_PRICE = 100

# 請在此處替換為你的 Google Sheet 網址
SHEET_URL = "https://docs.google.com/spreadsheets/d/1L3zv6EGs_JHfLqjWIcM10PJqlyu8bfBDcU6sfStVTlo/edit?usp=sharing"

# 建立連線
conn = st.connection("gsheets", type=GSheetsConnection)

# 讀取現有資料
try:
    df = conn.read(spreadsheet=SHEET_URL)
    # 確保資料格式正確，若為空則建立初始 DataFrame
    if df.empty:
        df = pd.DataFrame(columns=["姓名", "購買票數", "總金額", "訂購時間"])
except:
    df = pd.DataFrame(columns=["姓名", "購買票數", "總金額", "訂購時間"])

# 計算剩餘票數
total_sold = df["購買票數"].sum() if not df.empty else 0
remaining = TOTAL_TICKETS - total_sold

# --- 網頁介面 ---
st.title("🎫 專業雲端訂票系統")
st.write(f"目前剩餘票數：**{int(remaining)}** / {TOTAL_TICKETS} 張")

if remaining > 0:
    with st.form("booking_form", clear_on_submit=True):
        name = st.text_input("請輸入您的姓名")
        count = st.number_input("購買張數", min_value=1, max_value=int(remaining), step=1)
        submit = st.form_submit_button("確認結帳")

        if submit:
            if not name:
                st.error("❌ 請輸入姓名！")
            else:
                # 計算金額
                total_cost = count * TICKET_PRICE
                
                # 準備新資料列
                new_row = pd.DataFrame([{
                    "姓名": name,
                    "購買票數": count,
                    "總金額": total_cost,
                    "訂購時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                
                # 合併並更新到雲端
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                
                st.success(f"✅ 訂購成功！{name} 您好，總金額為 {total_cost} 元。")
                st.balloons()
                st.rerun() # 重新整理以更新餘票數字
else:
    st.error("🚫 票券已全數售罄，感謝支持！")

# --- 管理員檢視區 ---
st.markdown("---")
with st.expander("📊 查看即時銷售報表"):
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.write("目前尚無訂單紀錄。")

