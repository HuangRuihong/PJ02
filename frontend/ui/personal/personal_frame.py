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
        summary = self.system.get_user_summary(self.current_user)
        total = sum(summary.values())
        color = "#2ecc71" if total >= 0 else "#e74c3c"
        self.total_label.configure(text=f"總餘額: {'+' if total>=0 else ''}{total} TWD", text_color=color)
        
        for peer, amt in summary.items():
            if amt == 0: continue
            f = ctk.CTkFrame(self.scroll); f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=peer).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=str(amt), text_color="#2ecc71" if amt>0 else "#e74c3c").pack(side="right", padx=10)
