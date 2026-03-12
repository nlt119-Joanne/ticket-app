import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="2026 雲端訂票系統", page_icon="🎫")

# --- 認證與連線 ---
@st.cache_resource # 增加緩存，避免每次跑程式都重新連線 Google，速度會變快
def get_gspread_client():
    # 這裡檢查 secrets 是否存在
    if "gcp_service_account" not in st.secrets:
        st.error("❌ Secrets 中缺少 [gcp_service_account] 設定！")
        st.stop()
        
    # 讀取資訊並轉換為字典
    # 關鍵修正：使用 .to_dict() 確保格式完全正確
    info = st.secrets["gcp_service_account"]
    
    # 處理私鑰中的換行符號問題
    credentials = dict(info)
    if "private_key" in credentials:
        credentials["private_key"] = credentials["private_key"].replace("\\n", "\n")
    
    gc = gspread.service_account_from_dict(credentials)
    return gc

try:
    gc = get_gspread_client()
    # 確保 Secrets 裡也有 spreadsheet 設定
    if "connections" not in st.secrets or "gsheets" not in st.secrets["connections"]:
        st.error("❌ Secrets 中缺少 [connections.gsheets] 設定！")
        st.stop()
        
    sh = gc.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    wks = sh.get_worksheet(0) # 抓第一個分頁
except Exception as e:
    st.error(f"連線失敗: {e}")
    st.info("請檢查 Secrets 格式是否正確，以及 Google 試算表是否已共用給服務帳戶 Email。")
    st.stop()

# --- 讀取現有資料 ---
# 加上 try-except 防止試算表全空時報錯
try:
    data = wks.get_all_records()
    df = pd.DataFrame(data)
except Exception:
    df = pd.DataFrame(columns=["姓名", "購買票數", "總金額", "訂購時間"])

# --- 顯示與邏輯 ---
TOTAL_TICKETS = 10
# 確保欄位名稱與試算表一致
try:
    current_sold = df["購買票數"].sum()
except KeyError:
    current_sold = 0

remaining = TOTAL_TICKETS - current_sold

st.title("🎫 2026 專業訂票系統 (API版)")
st.metric("剩餘票數", f"{int(remaining)} 張", delta=None)

with st.form("order_form", clear_on_submit=True):
    name = st.text_input("您的姓名")
    count = st.number_input("購買張數", min_value=1, max_value=int(remaining) if remaining > 0 else 1, step=1)
    submit = st.form_submit_button("立即訂購")

    if submit:
        if remaining <= 0:
            st.error("❌ 抱歉，票已售罄！")
        elif not name:
            st.warning("⚠️ 請填寫姓名")
        elif count > remaining:
            st.error(f"❌ 剩餘票數不足（剩餘 {int(remaining)} 張）")
        else:
            # 寫入資料到最後一列
            new_row = [name, int(count), int(count * 100), datetime.now().strftime("%Y-%m-%d %H:%M")]
            wks.append_row(new_row)
            st.success(f"🎉 訂購成功！{name} 已購買 {count} 張票。")
            st.balloons()
            # 清除快取並重新整理
            st.cache_resource.clear()
            st.rerun()

st.markdown("---")
st.subheader("📊 訂單紀錄")
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.write("目前尚無訂購紀錄。")
