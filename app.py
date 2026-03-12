import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

# --- 頁面基本設定 ---
st.set_page_config(page_title="2026 雲端訂票系統", page_icon="🎫")

# --- 核心：連線函數 (針對單行 Secret 優化) ---
@st.cache_resource
def get_gspread_client():
    if "gcp_service_account" not in st.secrets:
        st.error("❌ Secrets 中缺少 [gcp_service_account] 設定！")
        st.stop()
        
    # 讀取資訊
    credentials = dict(st.secrets["gcp_service_account"])
    
    # 關鍵修正：將 Secrets 中的字面轉義字元 \n 轉為真正的換行符號
    if "private_key" in credentials:
        credentials["private_key"] = credentials["private_key"].replace("\\n", "\n")
        
    # 建立連線
    try:
        gc = gspread.service_account_from_dict(credentials)
        return gc
    except Exception as e:
        st.error(f"❌ 憑證驗證失敗，請檢查私鑰內容是否完整貼上：{e}")
        st.stop()

# --- 初始化連線與讀取資料 ---
try:
    gc = get_gspread_client()
    
    # 讀取試算表網址
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sh = gc.open_by_url(spreadsheet_url)
    wks = sh.get_worksheet(0) # 開啟工作表1
    
    # 讀取資料
    data = wks.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"⚠️ 連線失敗：{e}")
    st.info("💡 請確認：1. Secret 格式正確 2. 試算表已共用給服務帳戶 Email。")
    st.stop()

# --- 訂票邏輯 ---
TOTAL_TICKETS = 10

# 確保「購買票數」欄位存在並計算
try:
    current_sold = df["購買票數"].sum() if not df.empty else 0
except KeyError:
    current_sold = 0

remaining = TOTAL_TICKETS - current_sold

# --- 前端介面 ---
st.title("🎫 2026 專業訂票系統 (API版)")
st.metric("剩餘票數", f"{int(remaining)} 張")

with st.form("order_form", clear_on_submit=True):
    st.subheader("填寫訂單")
    name = st.text_input("您的姓名")
    count = st.number_input("購買張數", min_value=1, max_value=int(remaining) if remaining > 0 else 1, step=1)
    submit = st.form_submit_button("立即訂購")

    if submit:
        if remaining <= 0:
            st.error("❌ 票已售罄")
        elif not name:
            st.warning("⚠️ 請填寫姓名")
        else:
            # 準備寫入雲端的資料列
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = [name, int(count), int(count * 100), now]
            
            try:
                wks.append_row(new_row)
                st.success(f"🎉 訂購成功！{name} 已購買 {count} 張票。")
                st.balloons()
                
                # 清除快取並重新整理
                st.cache_resource.clear()
                st.rerun()
            except Exception as e:
                st.error(f"❌ 寫入失敗：{e}")

# --- 資料報表 ---
st.markdown("---")
st.subheader("📊 訂單紀錄清單")
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.write("目前尚無訂購紀錄。")
