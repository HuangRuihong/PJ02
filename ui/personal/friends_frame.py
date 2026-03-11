import customtkinter as ctk

class FriendsFrame(ctk.CTkFrame):
    def __init__(self, parent, system, current_user):
        super().__init__(parent, fg_color="transparent")
        self.system = system
        self.current_user = current_user
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(self.header, text="我的好友清單", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        ctk.CTkButton(self.header, text="+ 掃描好友名片", width=120, command=self.winfo_toplevel().scan_qr_from_file).pack(side="right", padx=10)
        self.scroll = ctk.CTkScrollableFrame(self, label_text="👥 所有的好友 (ID)")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

    def refresh(self):
        for w in self.scroll.winfo_children(): w.destroy()
        friends = self.system.get_friends(self.current_user)
        for fid in friends:
            f = ctk.CTkFrame(self.scroll); f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=f"👤 {fid}", font=ctk.CTkFont(size=14)).pack(side="left", padx=20, pady=10)
            ctk.CTkButton(f, text="發起記帳", width=80, command=lambda u=fid: self.winfo_toplevel().quick_charge(u)).pack(side="right", padx=10)
