import customtkinter as ctk
from tkcalendar import Calendar
from datetime import datetime
from ..components.dialogs import TransactionDetailDialog

class CalendarFrame(ctk.CTkFrame):
    def __init__(self, parent, system, current_user):
        super().__init__(parent, fg_color="transparent")
        self.system = system
        self.current_user = current_user
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        ctk.CTkLabel(self, text="帳務日曆", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, pady=20)
        
        # 日曆元件
        self.cal = Calendar(self, selectmode='day', 
                           year=datetime.now().year, 
                           month=datetime.now().month, 
                           day=datetime.now().day,
                           background="#242424", 
                           foreground="white", 
                           selectbackground="#1f538d")
        self.cal.grid(row=1, column=0, pady=10, padx=20, sticky="ew")
        self.cal.bind("<<CalendarSelected>>", self.on_date_select)
        
        # 該日明細
        self.detail_scroll = ctk.CTkScrollableFrame(self, label_text="選定日期交易明細")
        self.detail_scroll.grid(row=2, column=0, pady=10, padx=20, sticky="nsew")

    def on_date_select(self, event=None):
        self.refresh()

    def refresh(self, group_id=None):
        """刷新日曆分頁，顯示目前點選日期的所有帳務紀錄"""
        # 使用 selection_get() 直接取得 date 物件，避免字串解析失敗
        try:
            selected_date = self.cal.selection_get()
            search_date = selected_date.strftime('%Y-%m-%d')
            display_date = selected_date.strftime('%Y/%m/%d')
        except:
            # 備用方案：若尚未點選任何日期，預設為今天
            from datetime import date
            selected_date = date.today()
            search_date = selected_date.strftime('%Y-%m-%d')
            display_date = selected_date.strftime('%Y/%m/%d')
            
        # 清空舊畫面
        for w in self.detail_scroll.winfo_children(): w.destroy()
        
        # 設定捲軸標題顯示日期
        self.detail_scroll.configure(label_text=f"📅 {display_date} 交易明細")
        
        # 取得整體歷史紀錄並排序
        txs = self.system.get_personal_history(self.current_user)
        txs.sort(key=lambda x: str(x['timestamp']), reverse=True)
        
        found = False
        for tx in txs:
            # 判斷是否為該日交易 (timestamp 前 10 個字元為 YYYY-MM-DD)
            ts = str(tx["timestamp"])
            if ts.startswith(search_date):
                found = True
                # 建立交易卡片列 (比照 PersonalFrame 網格化)
                f = ctk.CTkFrame(self.detail_scroll, fg_color="#2c3e50" if tx.get('status') != 'SETTLED' else "transparent")
                f.pack(fill="x", pady=2, padx=5)
                f.grid_columnconfigure(1, weight=1) # 描述欄位拉伸
                
                # 1. 群組標籤 (小小的灰色)
                group_name = tx.get('group_name', '一般')
                ctk.CTkLabel(f, text=f"[{group_name}]", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
                
                # 2. 描述
                ctk.CTkLabel(f, text=tx['description'] or "一般支出", font=ctk.CTkFont(size=14), anchor="w").grid(row=0, column=1, padx=5, sticky="ew")
                
                # 3. 金額明細
                is_payer = (tx.get('payer_id') == self.current_user)
                amt_color = "#2ecc71" if is_payer else "#e74c3c"
                amt_text = f"+${tx['amount']}" if is_payer else f"-${tx['amount']}"
                
                amt_frame = ctk.CTkFrame(f, fg_color="transparent")
                amt_frame.grid(row=0, column=2, padx=15, sticky="e")
                
                ctk.CTkLabel(amt_frame, text=amt_text, text_color=amt_color, font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="e")
                
                status_map = {"CONFIRMED": "已確認", "PENDING": "待確認", "SETTLED": "已結清", "REJECTED": "已拒絕"}
                status_text = status_map.get(tx['status'], tx['status'])
                ctk.CTkLabel(amt_frame, text=status_text, font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="e")

                # 4. 透明點擊層
                click_btn = ctk.CTkButton(f, text="", fg_color="transparent", hover_color="#34495e", 
                                         command=lambda tid=tx['id']: self.show_detail(tid))
                click_btn.place(relx=0, rely=0, relwidth=1, relheight=1)
                
                # 提升所有標籤層級以避免被透明按鈕完全擋住點擊後的視覺回饋 (選用)
                for child in f.winfo_children():
                    if child != click_btn: child.lift()

        if not found:
            ctk.CTkLabel(self.detail_scroll, text="該日無任何交易明細記錄", text_color="gray").pack(pady=30)

    def show_detail(self, tid):
        """顯示交易詳情彈窗"""
        details = self.system.get_transaction_details(tid)
        if details:
            TransactionDetailDialog(
                self.winfo_toplevel(), details,
                system=self.system,
                current_user=self.current_user,
                refresh_cb=self.winfo_toplevel().refresh_ui
            )
