import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

# --- 頁面基本設定 ---
st.set_page_config(page_title="2026 雲端訂票系統", page_icon="🎫")

# --- 核心：修改後的連線函數 ---
@st.cache_resource # 使用快取，避免重複連線 Google API
def get_gspread_client():
    # 檢查 Secrets 是否存在
    if "gcp_service_account" not in st.secrets:
        st.error("❌ Secrets 中缺少 [gcp_service_account] 設定！")
        st.stop()
        
    # 讀取資訊並轉換為字典
    credentials = dict(st.secrets["gcp_service_account"])
    
    # 檢查私鑰內容是否正確（防止貼錯）
    if "-----BEGIN PRIVATE KEY-----" not in credentials.get("private_key", ""):
        st.error("❌ 私鑰格式錯誤！請確認 Secrets 中的 private_key 包含 BEGIN/END 字樣。")
        st.stop()
        
    # 建立連線
    try:
        gc = gspread.service_account_from_dict(credentials)
        return gc
    except Exception as e:
        st.error(f"❌ 憑證驗證失敗：{e}")
        st.stop()

# --- 初始化連線與讀取資料 ---
try:
    gc = get_gspread_client()
    
    # 檢查網址設定
    if "connections" not in st.secrets or "gsheets" not in st.secrets["connections"]:
        st.error("❌ Secrets 中缺少 [connections.gsheets] 的試算表網址！")
        st.stop()
        
    # 開啟試算表
    sh = gc.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    wks = sh.get_worksheet(0) # 開啟第一個分頁 (工作表1)
    
    # 讀取現有資料
    data = wks.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"⚠️ 連線失敗：{e}")
    st.info("💡 提醒：請確保已將 Google 服務帳號的 Email 加入到試算表的『共用』名單中（編輯者權限）。")
    st.stop()

# --- 訂票邏輯處理 ---
TOTAL_TICKETS = 10

# 計算已售出的票數 (對應你的欄位名稱：購買票數)
try:
    if not df.empty:
        current_sold = df["購買票數"].sum()
    else:
        current_sold = 0
except KeyError:
    st.warning("⚠️ 試算表中找不到『購買票數』欄位，請確認標題行正確。")
    current_sold = 0

remaining = TOTAL_TICKETS - current_sold

# --- 網頁前端顯示 ---
st.title("🎫 2026 專業訂票系統 (API版)")
st.metric("剩餘票數", f"{int(remaining)} 張")

with st.form("order_form", clear_on_submit=True):
    st.subheader("填寫訂單")
    name = st.text_input("您的姓名")
    count = st.number_input("購買張數", min_value=1, max_value=int(remaining) if remaining > 0 else 1, step=1)
    submit = st.form_submit_button("立即訂購")

    if submit:
        if remaining <= 0:
            st.error("❌ 抱歉，票已全數售罄！")
        elif not name:
            st.warning("⚠️ 請填寫訂購人姓名")
        elif count > remaining:
            st.error(f"❌ 剩餘票數不足（僅剩 {int(remaining)} 張）")
        else:
            # 準備新資料
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            total_price = count * 100
            new_row = [name, int(count), int(total_price), now]
            
            # 寫入資料到試算表最後一列
            try:
                wks.append_row(new_row)
                st.success(f"🎉 訂購成功！{name} 已購買 {count} 張票。")
                st.balloons()
                
                # 清除快取並重新整理頁面，確保抓到最新資料
                st.cache_resource.clear()
                st.rerun()
            except Exception as write_error:
                st.error(f"❌ 寫入雲端失敗：{write_error}")

# --- 底部報表顯示 ---
st.markdown("---")
st.subheader("📊 訂單紀錄清單")
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.write("目前尚無訂購紀錄，歡迎成為第一位訂票者！")
