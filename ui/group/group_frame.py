import customtkinter as ctk

class GroupFrame(ctk.CTkFrame):
    def __init__(self, parent, system):
        super().__init__(parent, fg_color="transparent")
        self.system = system
        self.setup_ui()

    def setup_ui(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=20, pady=10)
        
        self.info_label = ctk.CTkLabel(self.header, text="群組動態", font=ctk.CTkFont(size=20, weight="bold"))
        self.info_label.pack(side="left")
        
        self.add_btn = ctk.CTkButton(self.header, text="+ 記一筆", width=100, command=self.open_add_tx)
        self.add_btn.pack(side="right", padx=10)
        
        self.scroll = ctk.CTkScrollableFrame(self, label_text="最近活動")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

    def refresh(self, gid, gname, gcode, current_user):
        self.gid, self.current_user = gid, current_user
        self.info_label.configure(text=f"👥 {gname} (代碼: {gcode})")
        for w in self.scroll.winfo_children(): w.destroy()
        
        txs = self.system.get_group_transactions(gid)
        for tx in txs:
            f = ctk.CTkFrame(self.scroll); f.pack(fill="x", pady=5)
            # 簡化顯示
            ctk.CTkLabel(f, text=f"{tx['payer']} 支出 {tx['amount']}").pack(side="left", padx=10)
            if current_user in tx['pending_confirmations']:
                ctk.CTkButton(f, text="確認", width=60, command=lambda tid=tx['id']: self.master.master.confirm_tx(tid)).pack(side="right", padx=5)

    def open_add_tx(self):
        self.master.master.open_add_tx()
