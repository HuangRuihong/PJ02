import customtkinter as ctk
from PIL import Image

class QRDialog(ctk.CTkToplevel):
    def __init__(self, parent, qr_path, uid):
        super().__init__(parent)
        self.title("我的 QR Code 名片")
        self.geometry("400x500")
        ctk.CTkLabel(self, text=f"掃描以加入 {uid}", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        img = Image.open(qr_path)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 300))
        lbl = ctk.CTkLabel(self, image=ctk_img, text=""); lbl.pack(pady=10)
        ctk.CTkLabel(self, text=f"ID: {uid}", font=ctk.CTkFont(family="Consolas", size=16)).pack(pady=10)
        ctk.CTkButton(self, text="關閉", command=self.destroy).pack(pady=20)

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, login_callback):
        super().__init__(parent, fg_color="transparent")
        self.login_callback = login_callback
        ctk.CTkLabel(self, text="記帳系統", font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(100, 20))
        ctk.CTkLabel(self, text="歡迎回來，請輸入帳號進入系統", font=ctk.CTkFont(size=14), text_color="gray70").pack(pady=(0, 40))
        self.user_entry = ctk.CTkEntry(self, placeholder_text="使用者名稱", width=300, height=45); self.user_entry.pack(pady=10)
        self.remember_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self, text="記住帳號，下次自動登入", variable=self.remember_var).pack(pady=10)
        ctk.CTkButton(self, text="登入", width=300, height=50, command=self.submit).pack(pady=30)
    def submit(self):
        user = self.user_entry.get().strip()
        if user: self.login_callback(user, self.remember_var.get())
