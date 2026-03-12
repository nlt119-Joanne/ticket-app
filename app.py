import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 頁面設定
st.set_page_config(page_title="2026 雲端訂票系統", page_icon="🎫")

# 建立與 Google Sheets 的連線
conn = st.connection("gsheets", type=GSheetsConnection)

# 讀取現有資料 (ttl=0 表示不使用快取，確保看到最新訂單)
df = conn.read(ttl=0)

# 基礎變數
TOTAL_TICKETS = 10
total_sold = df.iloc[:, 1].sum() if not df.empty else 0
remaining = TOTAL_TICKETS - total_sold

st.title("🎫 全自動訂票系統")
st.write(f"目前剩餘票數：**{int(remaining)}** / {TOTAL_TICKETS} 張")

# 訂票表單
with st.form("booking_form", clear_on_submit=True):
    name = st.text_input("請輸入您的姓名")
    count = st.number_input("購買張數", min_value=1, max_value=int(remaining) if remaining > 0 else 1, step=1)
    submit = st.form_submit_button("確認結帳")

    if submit:
        if not name:
            st.error("❌ 請輸入姓名！")
        elif remaining <= 0:
            st.error("❌ 票已售罄！")
        else:
            # 建立新的一列資料
            new_data = pd.DataFrame([{
                "姓名": name,
                "購買票數": count,
                "總金額": count * 100,
                "訂購時間": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            
            # 將新資料與舊資料合併
            updated_df = pd.concat([df, new_data], ignore_index=True)
            
            # 關鍵步驟：更新回 Google Sheets
            conn.update(data=updated_df)
            
            st.success(f"✅ 訂購成功！{name} 您好，資料已寫入雲端。")
            st.balloons()
            st.rerun() # 自動重新整理顯示最新報表

# 顯示報表
st.markdown("---")
st.subheader("📊 最新訂單報表")
st.dataframe(df, use_container_width=True)
