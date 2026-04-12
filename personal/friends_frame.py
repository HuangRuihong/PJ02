import customtkinter as ctk

class FriendsFrame(ctk.CTkFrame):
    def __init__(self, parent, system, current_user):
        """
        初始化個人債務明細介面
        parent: 上層容器
        system: 後端核心 (DebtSystem)
        current_user: 當前登入的使用者名字
        """
        super().__init__(parent, fg_color="transparent")
        self.system = system
        self.current_user = current_user
        
        self.setup_ui()

    def setup_ui(self):
        """建立基本的介面骨架與標題"""
        self.grid_columnconfigure(0, weight=1)
        
        # 標題區塊
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(self.header, text="個人債務結算與往來對象", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        
        # 建立放卡片的捲動容器
        ctk.CTkLabel(self, text="您的欠帳 / 應收明細一覽", font=ctk.CTkFont(size=14, weight="bold"), text_color="gray").pack(padx=20, pady=(10,0), anchor="w")
        self.scroll = ctk.CTkFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

    def refresh(self, user_id=None):
        """重新整理或切換到這頁時，呼叫此函數重新繪製內容"""
        if user_id: self.current_user = str(user_id)
        
        if not hasattr(self, 'scroll'): return
        
        # 清空舊畫面
        for w in self.scroll.winfo_children(): w.destroy()
        
        # 獲取與所有人的債務總結 {friend_id: balance}
        summary = self.system.get_user_summary(self.current_user)
        
        # 過濾掉已經完全結清 (餘額為 0) 的對象
        active_debts = {fid: bal for fid, bal in summary.items() if bal != 0}
        
        if not active_debts:
            ctk.CTkLabel(self.scroll, text="目前沒有任何未結清的欠帳或應收款項，財富自由！", text_color="gray").pack(pady=40)
            return

        # 根據與該對象的「欠債/應收金額絕對值」由高到低降序排列
        sorted_fids = sorted(active_debts.keys(), key=lambda fid: abs(active_debts[fid]), reverse=True)

        for fid in sorted_fids:
            bal = active_debts[fid]
            self.create_debt_card(fid, bal)

    def create_debt_card(self, fid, bal):
        # 極簡風卡片
        card = ctk.CTkFrame(self.scroll, fg_color="#2c2c2c", corner_radius=6)
        card.pack(fill="x", pady=3, padx=10)
        
        # --- 單行資訊設計 ---
        ctk.CTkLabel(card, text=str(fid), font=ctk.CTkFont(size=15, weight="bold"), width=100, anchor="w").pack(side="left", padx=(15, 10), pady=10)
        
        if bal > 0:
            status_text = f"他欠你 ${bal:,}"
            status_color = "#2ecc71"
        else:
            status_text = f"你欠他 ${abs(bal):,}"
            status_color = "#e74c3c"
            
        ctk.CTkLabel(card, text=status_text, text_color=status_color, font=ctk.CTkFont(size=14, weight="bold"), width=120, anchor="w").pack(side="left", padx=10, pady=10)
        
        # --- 卡片右側按鈕區 ---
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=(0, 10), pady=8)
        
        ctk.CTkButton(btn_frame, text="記一筆", width=60, height=28, fg_color="#1f538d", hover_color="#2980b9",
                    command=lambda u=fid: self.winfo_toplevel().quick_charge(u)).pack(side="left", padx=3)
        
        if bal > 0:
            def send_dunning(target=fid, amt=bal):
                from tkinter import messagebox
                messagebox.showinfo("催款通知", f"已發送催款提醒給 {target} (欠款 ${amt:,})", parent=self.winfo_toplevel())
            
            ctk.CTkButton(btn_frame, text="催款", width=60, height=28, fg_color="#d35400", hover_color="#e67e22",
                          command=send_dunning).pack(side="left", padx=3)
        elif bal < 0:
            ctk.CTkButton(btn_frame, text="我要還款", width=70, height=28, fg_color="#27ae60", hover_color="#2ecc71",
                          command=lambda u=fid, amt=abs(bal): self.open_repay_dialog(u, amt)).pack(side="left", padx=3)

    def open_repay_dialog(self, target_friend, amount):
        from tkinter import messagebox
        dialog = ctk.CTkToplevel(self.winfo_toplevel())
        dialog.title("我要還款")
        dialog.geometry("350x300")
        dialog.attributes("-topmost", True)
        dialog.grab_set()
        dialog.after(10, dialog.lift)
        
        ctk.CTkLabel(dialog, text=f"向 {target_friend} 結清 ${amount:,}", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20,10))
        ctk.CTkLabel(dialog, text="請選擇您的還款方式，對方確認後即會正式銷帳：", text_color="gray").pack(pady=5)
        
        method_var = ctk.StringVar(value="現金")
        ctk.CTkRadioButton(dialog, text="現金交付", variable=method_var, value="現金").pack(pady=5)
        ctk.CTkRadioButton(dialog, text="銀行轉帳 / LINE Pay", variable=method_var, value="轉帳").pack(pady=5)
        ctk.CTkRadioButton(dialog, text="其他代墊抵銷", variable=method_var, value="其他抵銷").pack(pady=5)
        
        def submit():
            # 取得我欠這個對象的所有帳單
            payables, _ = self.system.get_personal_debts(self.current_user)
            tx_ids = [p['tx_id'] for p in payables if p['creditor'] == target_friend]
            
            if not tx_ids:
                messagebox.showerror("錯誤", "找不到相對應的待結清帳單！", parent=dialog)
                dialog.destroy()
                return
                
            if self.system.request_settlement(self.current_user, target_friend, amount, method_var.get(), tx_ids):
                messagebox.showinfo("申請已送出", f"[OK] 已把「{method_var.get()}結清」的通知發送給 {target_friend}！\n對方確認後就會自動消除負債。", parent=self.winfo_toplevel())
                self.winfo_toplevel().refresh_ui()
            else:
                messagebox.showerror("錯誤", "發生未知錯誤，請重試。", parent=dialog)
            dialog.destroy()
            
        ctk.CTkButton(dialog, text="確認送出結清申請", command=submit).pack(pady=20)
