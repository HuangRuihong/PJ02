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
        # 日曆改為顯示使用者的整體歷史紀錄 (不侷限於單一群組)
        selected_date = self.cal.get_date()
        try:
            date_obj = datetime.strptime(selected_date, '%m/%d/%y')
            search_date = date_obj.strftime('%Y-%m-%d')
            display_date = date_obj.strftime('%Y/%m/%d')
        except:
            search_date = selected_date
            display_date = selected_date
            
        for w in self.detail_scroll.winfo_children(): w.destroy()
        
        txs = self.system.get_personal_history(self.current_user)
        found = False
        for tx in txs:
            # 篩選該日期的交易 (SQLite 存儲通常為 YYYY-MM-DD...)
            if str(tx["timestamp"]).startswith(search_date):
                found = True
                f = ctk.CTkFrame(self.detail_scroll); f.pack(fill="x", pady=2, padx=5)
                payer_text = "你付了" if tx.get('payer_id') == self.current_user else f"{tx.get('payer_id')} 付了"
                ctk.CTkLabel(f, text=f"{tx['description'] if tx['description'] else '無描述'}", width=150, anchor="w").pack(side="left", padx=10)
                ctk.CTkLabel(f, text=f"{payer_text} ${tx['amount']}", width=150).pack(side="left", padx=10)
                status_map = {"CONFIRMED": "已確認", "PENDING": "待確認", "SETTLED": "已結清", "REJECTED": "已拒絕"}
                status_text = status_map.get(tx['status'], tx['status'])
                ctk.CTkLabel(f, text=status_text, text_color="#3498db").pack(side="right", padx=10)

                # 使整列可點擊
                click_btn = ctk.CTkButton(f, text="", fg_color="transparent", hover_color="#2c2c2c", 
                                         command=lambda tid=tx['id']: self.show_detail(tid))
                click_btn.place(relx=0, rely=0, relwidth=1, relheight=1)
                for child in f.winfo_children():
                    if child != click_btn: child.lift()

        if not found:
            ctk.CTkLabel(self.detail_scroll, text="該日無相關的交易記錄").pack(pady=20)

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
