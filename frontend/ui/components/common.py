import customtkinter as ctk

# common.py 存放通用 UI 組件

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, login_callback):
        super().__init__(parent, fg_color="transparent")
        self.login_callback = login_callback
        ctk.CTkLabel(self, text="記帳系統", font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(100, 20))
        ctk.CTkLabel(self, text="歡迎回來，請輸入帳號進入系統", font=ctk.CTkFont(size=14), text_color="gray70").pack(pady=(0, 40))
        self.user_entry = ctk.CTkEntry(self, placeholder_text="使用者名稱", width=300, height=45); self.user_entry.pack(pady=10)
        self.remember_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self, text="記住帳號，下次自動登入", variable=self.remember_var).pack(pady=10)
        
        self.login_btn = ctk.CTkButton(self, text="進入系統", width=300, height=50, command=self.submit, 
                                       fg_color="#1f538d", hover_color="#14375e", font=ctk.CTkFont(weight="bold"))
        self.login_btn.pack(pady=30)
    def submit(self):
        user = self.user_entry.get().strip()
        if user: self.login_callback(user, self.remember_var.get())
