import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="2026 雲端訂票系統", page_icon="🎫")

# 認證與連線
def get_gspread_client():
    # 從 Secrets 讀取完整 JSON 資訊
    credentials = dict(st.secrets["gcp_service_account"])
    # 這裡的處理是為了讓私鑰格式正確
    credentials["private_key"] = credentials["private_key"].replace("\\n", "\n")
    gc = gspread.service_account_from_dict(credentials)
    return gc

try:
    gc = get_gspread_client()
    sh = gc.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    wks = sh.get_worksheet(0) # 抓第一個分頁
except Exception as e:
    st.error(f"連線失敗: {e}")
    st.stop()

# 讀取現有資料
data = wks.get_all_records()
df = pd.DataFrame(data)

# 顯示剩餘票數
remaining = 10 - (df["購買票數"].sum() if not df.empty else 0)

st.title("🎫 2026 專業訂票系統 (API版)")
st.metric("剩餘票數", f"{int(remaining)} 張")

with st.form("order_form", clear_on_submit=True):
    name = st.text_input("您的姓名")
    count = st.number_input("購買張數", min_value=1, max_value=int(remaining) if remaining > 0 else 1)
    submit = st.form_submit_button("立即訂購")

    if submit and remaining >= count:
        if name:
            # 寫入資料到最後一列
            wks.append_row([name, count, count * 100, datetime.now().strftime("%Y-%m-%d %H:%M")])
            st.success("🎉 訂購成功！資料已即時同步。")
            st.balloons()
            st.rerun()
        else:
            st.warning("請填寫姓名")

st.markdown("---")
st.subheader("📊 訂單紀錄")
st.dataframe(df, use_container_width=True)
