import customtkinter as ctk
from datetime import datetime
from shared.dialogs import TransactionDetailDialog
from shared.models import Category

class PersonalFrame(ctk.CTkFrame):
    def __init__(self, parent, system, current_user):
        """
        初始化個人介面
        parent: 上層容器
        system: 隊友寫的後端核心
        current_user: 當前登入的使用者名字
        """
        super().__init__(parent, fg_color="transparent")
        self.system = system
        self.current_user = current_user
        
        # 將原捲軸容器改為普通容器，由最外層主分頁捲動
        self.main_scroll = ctk.CTkFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 標題
        self.title_label = ctk.CTkLabel(self.main_scroll, text=f"{self.current_user} 的個人帳單儀表板", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(10, 20), anchor="w", padx=20)
        
        # 準備三個主要區塊的容器
        self.dashboard_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.dashboard_frame.pack(fill="x", padx=10, pady=10)
        
        self.inbox_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.inbox_frame.pack(fill="x", padx=10, pady=10)
        
        self.history_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.history_frame.pack(fill="x", padx=10, pady=10)

    def _format_date(self, raw, fmt='%Y/%m/%d'):
        """統一的日期解析與格式化 (一行化優化)"""
        if not raw: return "----/--/--"
        try:
            dt = raw if isinstance(raw, datetime) else (datetime.fromisoformat(str(raw)) if " " in str(raw) or "T" in str(raw) else datetime.strptime(str(raw)[:10], '%Y-%m-%d'))
            return dt.strftime(fmt)
        except: return str(raw)[:10].replace('-', '/')

    def load_real_data(self):
        """同步載入後端數據並格式化 (Person A 壓縮版)"""
        payables, receivables = self.system.get_personal_debts(self.current_user)
        self.pending_inbox = [{
            "id": d['tx_id'], "payer": d['creditor'],
            "amount": d['amount'], "desc": d['desc'] or "無描述",
            "time": self._format_date(d['date']), "status": "PENDING", 
            "type": d.get('type'), "loc": d.get('loc'), "category": d.get('category', 'OTHER')
        } for d in payables if d['status'] == 'PENDING']
        
        self.history_data = self.system.get_personal_history(self.current_user)
        summary = self.system.get_user_summary(self.current_user)
        total_assets = sum(summary.values())
        self.dashboard_data = {"total_assets": total_assets, "receivables": sum(v for v in summary.values() if v > 0), "payables": sum(v for v in summary.values() if v < 0)}

    def do_confirm(self, tx_id, tx_type=None, loc_str=None, payer_id=None):
        """處理確認交易連動 / 審核結清申請 (壓縮版)"""
        from tkinter import messagebox
        res = False
        if tx_type == "REPAY_REQUEST":
            if self.system.settle_specific_debts(payer_id, self.current_user, loc_str.split(",") if loc_str else []):
                self.system.confirm_transaction(self.current_user, tx_id, status="SETTLED")
                res = True
        else: res = self.system.confirm_transaction(self.current_user, tx_id)
        
        if res: messagebox.showinfo("成功", "操作已成功執行！", parent=self.winfo_toplevel()); self.winfo_toplevel().refresh_ui()
        else: messagebox.showerror("錯誤", "處理失敗！", parent=self.winfo_toplevel())

    def do_reject(self, tx_id, tx_type=None):
        """處理拒絕交易"""
        if self.system.reject_transaction(self.current_user, tx_id):
            self.winfo_toplevel().refresh_ui()

    def build_dashboard(self):
        """畫出第一區塊：數據卡片儀表板"""
        d = self.dashboard_data
        cards_container = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        cards_container.pack(fill="x", padx=10, pady=10)
        cards_container.grid_columnconfigure((0,1,2), weight=1)
        
        for i, (title, val, color) in enumerate([("總資產 (淨額)", d['total_assets'], "#1f538d"), ("累計應收", d['receivables'], "#2ecc71"), ("累計應付", d['payables'], "#e74c3c")]):
            card = ctk.CTkFrame(cards_container, fg_color=color)
            card.grid(row=0, column=i, padx=5, sticky="ew")
            ctk.CTkLabel(card, text=title, text_color="gray90").pack(pady=(10, 0))
            ctk.CTkLabel(card, text=f" ${val:+,}", font=ctk.CTkFont(size=24, weight="bold"), text_color="white").pack(pady=(5, 15))

    def build_inbox(self):
        """畫出第二區塊：待確認通知匣"""
        ctk.CTkLabel(self.inbox_frame, text="待辦事項 (需要你驗證的帳款)", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(20, 10))
        if not self.pending_inbox:
            ctk.CTkLabel(self.inbox_frame, text="目前沒有需要驗證的帳款喔！", text_color="gray").pack(pady=10); return
            
        for item in self.pending_inbox:
            card = ctk.CTkFrame(self.inbox_frame, border_width=1, border_color="#e67e22")
            card.pack(fill="x", pady=5)
            info = ctk.CTkFrame(card, fg_color="transparent"); info.pack(side="left", fill="both", expand=True, padx=15, pady=10)
            
            # 分類圖示
            cat = Category.__members__.get(item.get('category', 'OTHER'), Category.OTHER)
            ctk.CTkLabel(info, text=cat.icon, font=ctk.CTkFont(size=20), text_color=cat.color).pack(side="left", padx=(0, 10))
            
            text_box = ctk.CTkFrame(info, fg_color="transparent")
            text_box.pack(side="left", fill="both", expand=True)
            ctk.CTkLabel(text_box, text=f"發起人: {item['payer']} | {item['time']}", font=ctk.CTkFont(size=11), text_color="gray70").pack(anchor="w")
            ctk.CTkLabel(text_box, text=f"{item['desc']} ({'還款' if item['type'] in ['REPAY_REQUEST', 'SETTLEMENT'] else '請款'}: ${item['amount']})", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w")
            
            btns = ctk.CTkFrame(card, fg_color="transparent"); btns.pack(side="right", padx=15)
            ctk.CTkButton(btns, text="確認", width=60, fg_color="#27ae60", command=lambda x=item: self.do_confirm(x['id'], x['type'], x['loc'], x['payer'])).pack(side="left", padx=5)
            ctk.CTkButton(btns, text="有誤", width=60, fg_color="#c0392b", command=lambda x=item: self.do_reject(x['id'], x['type'])).pack(side="left", padx=5)
            
            # 懸停效果
            card.bind("<Enter>", lambda e, c=card: c.configure(fg_color="#2c2c2c"))
            card.bind("<Leave>", lambda e, c=card: c.configure(fg_color="transparent"))
            for w in [info]+list(info.winfo_children()): 
                w.bind("<Button-1>", lambda e, tid=item['id']: self.show_detail(tid)); w.configure(cursor="hand2")

    def build_history(self):
        """畫出第三區塊：歷史紀錄清單"""
        ctk.CTkLabel(self.history_frame, text="最近的帳務紀錄", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(20, 10))
        if not self.history_data:
            ctk.CTkLabel(self.history_frame, text="尚無任何歷史紀錄。", text_color="gray").pack(pady=10); return

        last_date = None
        for item in self.history_data[:20]:
            curr_date = self._format_date(item['timestamp'], '%m月%d日')
            if curr_date != last_date:
                sep = ctk.CTkFrame(self.history_frame, fg_color="transparent"); sep.pack(fill="x", pady=(10, 2))
                ctk.CTkLabel(sep, text=f"{curr_date} ------------------", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70").pack(side="left", padx=10)
                last_date = curr_date

            hf = ctk.CTkFrame(self.history_frame, fg_color="transparent", height=40); hf.pack(fill="x", pady=1); hf.grid_propagate(False)
            hf.grid_rowconfigure(0, weight=1); hf.grid_columnconfigure((0,1), minsize=60); hf.grid_columnconfigure(3, weight=1)
            
            from shared.models import TransactionStatus
            st_color, st_text = TransactionStatus.get_ui_info(item['status'])
            ctk.CTkLabel(hf, text=st_text, fg_color=st_color, text_color="white", corner_radius=4, width=60, font=ctk.CTkFont(size=10)).grid(row=0, column=0, padx=5)
            
            # 分類圖示
            cat = Category.__members__.get(item.get('category', 'OTHER'), Category.OTHER)
            ctk.CTkLabel(hf, text=cat.icon, text_color=cat.color, width=25).grid(row=0, column=1)

            ctk.CTkLabel(hf, text=f"[{item['group_name']}]", text_color="gray", font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=5, sticky="w")
            ctk.CTkLabel(hf, text=item['description'], anchor="w").grid(row=0, column=3, padx=5, sticky="ew")
            
            amt_color = "#2ecc71" if item['payer_id'] == self.current_user else "#e74c3c"
            ctk.CTkLabel(hf, text=f"${item['amount']:,}", text_color=amt_color, font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=15, sticky="e")

            for w in [hf]+list(hf.winfo_children()):
                w.bind("<Button-1>", lambda e, tid=item['id']: self.show_detail(tid))
                w.bind("<Enter>", lambda e, h=hf: h.configure(fg_color="#2c3e50"))
                w.bind("<Leave>", lambda e, h=hf: h.configure(fg_color="transparent"))
                w.configure(cursor="hand2")

    def show_detail(self, tid):
        from shared.dialogs import TransactionDetailDialog
        d = self.system.get_transaction_details(tid)
        if d: TransactionDetailDialog(self.winfo_toplevel(), d, system=self.system, current_user=self.current_user, refresh_cb=self.winfo_toplevel().refresh_ui)

    def refresh(self):
        for w in [self.dashboard_frame, self.inbox_frame, self.history_frame]:
            for child in w.winfo_children(): child.destroy()
        self.load_real_data(); self.build_dashboard(); self.build_inbox(); self.build_history()
