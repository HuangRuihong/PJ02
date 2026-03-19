import customtkinter as ctk
from tkcalendar import Calendar
from datetime import datetime

class CalendarFrame(ctk.CTkFrame):
    def __init__(self, parent, system, current_user):
        super().__init__(parent, fg_color="transparent")
        self.system = system
        self.current_user = current_user
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        ctk.CTkLabel(self, text="📅 帳務日曆", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, pady=20)
        
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
            date_str = date_obj.strftime('%Y-%m-%d')
        except:
            date_str = selected_date # fallback
            
        for w in self.detail_scroll.winfo_children(): w.destroy()
        
        txs = self.system.get_personal_history(self.current_user)
        found = False
        for tx in txs:
            if str(tx["time"]).startswith(date_str):
                found = True
                f = ctk.CTkFrame(self.detail_scroll); f.pack(fill="x", pady=2, padx=5)
                payer_text = "你付了" if tx.get('payer') == self.current_user else f"{tx.get('payer')} 付了"
                ctk.CTkLabel(f, text=f"{tx['desc'] if tx['desc'] else '無描述'}", width=150, anchor="w").pack(side="left", padx=10)
                ctk.CTkLabel(f, text=f"{payer_text} ${tx['amount']}", width=150).pack(side="left", padx=10)
                ctk.CTkLabel(f, text=f"{tx['status']}", text_color="#3498db").pack(side="right", padx=10)
        
        if not found:
            ctk.CTkLabel(self.detail_scroll, text="該日無相關的交易記錄").pack(pady=20)
