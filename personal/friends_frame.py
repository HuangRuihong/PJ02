import customtkinter as ctk
from tkinter import messagebox as mbox

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
            ctk.CTkLabel(self.scroll, text="目前沒有任何未結清的欠帳或應收款項，財富自由！", text_color="gray").pack(pady=40); return

        for fid in sorted(active_debts.keys(), key=lambda x: abs(active_debts[x]), reverse=True):
            self.create_debt_card(fid, active_debts[fid])

    def create_debt_card(self, fid, bal):
        card = ctk.CTkFrame(self.scroll, fg_color="#2c2c2c", corner_radius=6); card.pack(fill="x", pady=3, padx=10)
        ctk.CTkLabel(card, text=str(fid), font=ctk.CTkFont(size=15, weight="bold"), width=100, anchor="w").pack(side="left", padx=(15, 10), pady=10)
        
        status_text, status_color = (f"他欠你 ${bal:,}", "#2ecc71") if bal > 0 else (f"你欠他 ${abs(bal):,}", "#e74c3c")
        ctk.CTkLabel(card, text=status_text, text_color=status_color, font=ctk.CTkFont(size=14, weight="bold"), width=120, anchor="w").pack(side="left", padx=10)
        
        btns = ctk.CTkFrame(card, fg_color="transparent"); btns.pack(side="right", padx=10)
        ctk.CTkButton(btns, text="記一筆", width=60, height=28, command=lambda: self.winfo_toplevel().quick_charge(fid)).pack(side="left", padx=3)
        if bal > 0:
            ctk.CTkButton(btns, text="催款", width=60, height=28, fg_color="#d35400", command=lambda: mbox.showinfo("催款", f"已提醒 {fid} 欠款 ${bal:,}", parent=self.winfo_toplevel())).pack(side="left", padx=3)
        else:
            ctk.CTkButton(btns, text="還款", width=60, height=28, fg_color="#27ae60", command=lambda: self.open_repay_dialog(fid, abs(bal))).pack(side="left", padx=3)

    def open_repay_dialog(self, target, amount):
        dialog = ctk.CTkToplevel(self.winfo_toplevel()); dialog.title("還款"); dialog.geometry("350x280"); dialog.grab_set()
        ctk.CTkLabel(dialog, text=f"向 {target} 結清 ${amount:,}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        method_var = ctk.StringVar(value="現金")
        for m in ["現金交付", "轉帳 / LINE Pay", "其他抵銷"]:
            ctk.CTkRadioButton(dialog, text=m, variable=method_var, value=m).pack(pady=2)
        
        def submit():
            p, _ = self.system.get_personal_debts(self.current_user)
            ids = [i['tx_id'] for i in p if i['creditor'] == target]
            if self.system.request_settlement(self.current_user, target, amount, method_var.get(), ids):
                mbox.showinfo("成功", f"申請已送出！", parent=self.winfo_toplevel()); self.winfo_toplevel().refresh_ui()
            dialog.destroy()
        ctk.CTkButton(dialog, text="確認送出", command=submit).pack(pady=20)

