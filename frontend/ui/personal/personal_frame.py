import customtkinter as ctk

class PersonalFrame(ctk.CTkFrame):
    def __init__(self, parent, system, current_user):
        super().__init__(parent, fg_color="transparent")
        self.system = system
        self.current_user = current_user
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="個人帳單摘要", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        self.balance_frame = ctk.CTkFrame(self)
        self.balance_frame.pack(fill="x", padx=20, pady=10)
        
        self.total_label = ctk.CTkLabel(self.balance_frame, text="總餘額: 計算中...", font=ctk.CTkFont(size=16))
        self.total_label.pack(pady=20)
        
        self.scroll = ctk.CTkScrollableFrame(self, label_text="明細")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

    def refresh(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        # 1. 債務摘要區
        summary = self.system.get_user_summary(self.current_user)
        total = sum(summary.values())
        color = "#2ecc71" if total >= 0 else "#e74c3c"
        self.total_label.configure(text=f"總餘額統計: {'+' if total>=0 else ''}{total} TWD", text_color=color)
        
        sum_f = ctk.CTkFrame(self.scroll, fg_color="transparent"); sum_f.pack(fill="x", pady=5)
        ctk.CTkLabel(sum_f, text="--- 債務與代墊摘要 ---", font=ctk.CTkFont(weight="bold")).pack()
        
        for peer, amt in summary.items():
            if amt == 0: continue
            f = ctk.CTkFrame(self.scroll); f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=peer).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=str(amt), text_color="#2ecc71" if amt>0 else "#e74c3c").pack(side="right", padx=10)

        # 2. 個人支出流水區 (NEW)
        ctk.CTkLabel(self.scroll, text="\n--- 我的支出流水 (含私帳) ---", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        history = self.system.get_personal_history(self.current_user)
        if not history:
            ctk.CTkLabel(self.scroll, text="目前尚無支出紀錄", text_color="gray").pack()
        else:
            for tx in history:
                hf = ctk.CTkFrame(self.scroll); hf.pack(fill="x", pady=2, padx=5)
                # 顯示群組名稱或標記為私帳
                grp_display = "🔐 個人私帳" if tx['group'] == 'PERSONAL' else f"👥 {tx['group']}"
                ctk.CTkLabel(hf, text=f"{tx['time'][:10]}", width=80).pack(side="left", padx=5)
                ctk.CTkLabel(hf, text=tx['desc'] or "無描述", width=120, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(hf, text=grp_display, width=100, text_color="gray").pack(side="left", padx=5)
                ctk.CTkLabel(hf, text=f"${tx['amount']}", text_color="#e74c3c").pack(side="right", padx=10)
