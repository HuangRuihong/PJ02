import customtkinter as ctk
import qrcode
from PIL import Image
import os

class FriendsFrame(ctk.CTkFrame):
    def __init__(self, parent, system, current_user):
        """
        初始化我的好友介面
        parent: 上層容器
        system: 隊友寫的後端核心
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
        
        ctk.CTkLabel(self.header, text="👥 我的好友清單與結算狀態", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        
        # 按鈕容器 (放在右邊)
        btn_container = ctk.CTkFrame(self.header, fg_color="transparent")
        btn_container.pack(side="right")

        # 顯示自己的 QR Code 按鈕
        self.my_qr_btn = ctk.CTkButton(btn_container, text="📱 我的 QR 名片", width=120, fg_color="#8e44ad", hover_color="#9b59b6",
                                       command=self.show_mock_qr)
        self.my_qr_btn.pack(side="left", padx=5)
        
        # 掃描名片按鈕 (改用我們自己的 Mock 版本，方便測試不報錯)
        self.scan_btn = ctk.CTkButton(btn_container, text="🔍 掃描好友名片", width=120, 
                                      command=self.mock_scan_qr)
        self.scan_btn.pack(side="left", padx=5)
        
        # 建立放好友卡片的大捲軸
        self.scroll = ctk.CTkScrollableFrame(self, label_text="好友關係一覽")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

    def show_mock_qr(self):
        """產生並顯示專屬於當前使用者的 QR Code 彈出視窗"""
        # 1. 產生 QR Code 圖片
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(self.current_user) # 將目前使用者的名字塞入 QR 碼
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 先存到本地暫存，給 customtkinter 讀取
        temp_path = "temp_my_qr.png"
        img.save(temp_path)
        
        # 2. 建立新視窗顯示圖片
        dialog = ctk.CTkToplevel(self)
        dialog.title("我的名片")
        dialog.geometry("350x450")
        dialog.attributes("-topmost", True) # 保持在最上層
        
        ctk.CTkLabel(dialog, text=f"讓好友掃描此 QR Code", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        pil_img = Image.open(temp_path)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(250, 250))
        ctk.CTkLabel(dialog, image=ctk_img, text="").pack(pady=10)
        
        ctk.CTkLabel(dialog, text=f"您的 ID: {self.current_user}", text_color="gray", font=ctk.CTkFont(size=14)).pack(pady=10)
        ctk.CTkButton(dialog, text="關閉", command=dialog.destroy).pack(pady=10)

    def mock_scan_qr(self):
        """模擬掃描 QR Code 並成功加入好友的互動視窗"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("掃描名片")
        dialog.geometry("350x250")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text="📷 正在開啟鏡頭 / 選擇相片...", font=ctk.CTkFont(size=16)).pack(pady=20)
        ctk.CTkLabel(dialog, text="(目前為測試模式：請直接輸入好友 ID)", text_color="gray").pack()
        
        input_id = ctk.CTkEntry(dialog, placeholder_text="例如: 新室友D")
        input_id.pack(pady=15, padx=20, fill="x")
        
        def confirm_scan():
            new_friend = input_id.get().strip()
            if new_friend:
                print(f"[掃描成功] 已辨識到 QR Code，準備加入好友：{new_friend}")
                # 這裡把新好友動態加入 Mock 資料，並馬上重新整理畫面！
                self.mock_friends.append({"id": new_friend, "balance": 0, "overdue_days": 0})
                self.refresh() # 重繪好友卡片列表
                dialog.destroy()
        
        ctk.CTkButton(dialog, text="確認掃描", command=confirm_scan, fg_color="#27ae60").pack(pady=10)
    def load_mock_data(self):
        """
        載入假資料 (Mock Data)
        用來取代 self.system.get_friends(self.current_user) 和 get_user_summary 的複雜計算。
        等後端資料庫寫好後，再把它們換掉。
        """
        self.mock_friends = [
            {
                "id": "室友A", 
                "balance": 500,     # >0 代表他欠我錢 (應收)
                "overdue_days": 2   # 逾期天數 (大於 0 代表已逾期，對應企劃書的【自動化催告】)
            },
            {
                "id": "室友B", 
                "balance": -150,    # <0 代表我欠他錢 (應付)
                "overdue_days": 0
            },
            {
                "id": "學長C", 
                "balance": 0,       # =0 代表已結清
                "overdue_days": 0
            }
        ]

    def refresh(self):
        """重新整理或切換到這頁時，呼叫此函數重新繪製內容"""
        # 清空舊畫面
        for w in self.scroll.winfo_children(): w.destroy()
        
        # 載入假資料
        self.load_mock_data()
        
        if not self.mock_friends:
            ctk.CTkLabel(self.scroll, text="你目前還沒加入任何好友喔！", text_color="gray").pack(pady=20)
            return

        for friend in self.mock_friends:
            self.create_friend_card(friend)

    def create_friend_card(self, friend):
        """畫出【單一位好友】的詳細卡片與對應按鈕"""
        fid = friend["id"]
        bal = friend["balance"]
        overdue = friend["overdue_days"]
        
        # 卡片外框設定：如果這張卡片有人逾期，邊框就設定為搶眼的橘紅色警告
        border_col = "#e74c3c" if overdue > 0 else ("#34495e" if bal == 0 else "#2c3e50")
        card = ctk.CTkFrame(self.scroll, border_width=1, border_color=border_col)
        card.pack(fill="x", pady=5, padx=5)
        
        # --- 卡片左側：大頭貼與名字 ---
        left_area = ctk.CTkFrame(card, fg_color="transparent")
        left_area.pack(side="left", padx=15, pady=15)
        ctk.CTkLabel(left_area, text=f"👤 {fid}", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        
        # --- 卡片中間：目前的債務狀態文字 (根據金額變換顏色) ---
        mid_area = ctk.CTkFrame(card, fg_color="transparent")
        mid_area.pack(side="left", fill="both", expand=True, padx=20, pady=15)
        
        if bal > 0:
            status_text = f"他欠你 ${bal}"
            status_color = "#2ecc71" # 綠色
        elif bal < 0:
            status_text = f"你欠他 ${abs(bal)}"
            status_color = "#e74c3c" # 紅色
        else:
            status_text = "目前已結清"
            status_color = "gray"    # 灰色
            
        ctk.CTkLabel(mid_area, text=status_text, text_color=status_color, font=ctk.CTkFont(size=16)).pack(anchor="w")
        
        # [企劃書亮點] 如果這筆帳有人逾期了，就顯示法制警告標語！
        if overdue > 0:
            warning_text = f"🚨 系統偵測：有帳款已逾期 {overdue} 天未結清"
            ctk.CTkLabel(mid_area, text=warning_text, text_color="#e67e22", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(5,0))
            
        # --- 卡片右側：情境按鈕區 ---
        right_area = ctk.CTkFrame(card, fg_color="transparent")
        right_area.pack(side="right", padx=15, pady=15)
        
        # 預設一定會有的功能：「發起記帳」
        # (直接沿用原本的 self.winfo_toplevel().quick_charge)
        ctk.CTkButton(right_area, text="📝 發起記帳", width=90, fg_color="#1f538d",
                      command=lambda u=fid: self.winfo_toplevel().quick_charge(u)).pack(side="left", padx=5)
        
        # 特殊情境按鈕 1：別人欠我錢 (顯示「一鍵催告」)
        if bal > 0:
            ctk.CTkButton(right_area, text="📨 發送催告", width=90, fg_color="#d35400", hover_color="#e67e22",
                          command=lambda u=fid: print(f"[警示系統] 已對 {u} 發出系統催告通知！")).pack(side="left", padx=5)
                          
        # 特殊情境按鈕 2：我欠別人錢 (顯示「立即結清」)
        elif bal < 0:
            ctk.CTkButton(right_area, text="💳 立即結清", width=90, fg_color="#27ae60", hover_color="#2ecc71",
                          command=lambda u=fid: print(f"[系統提示] 進入結帳金流流程，準備還給 {u}...")).pack(side="left", padx=5)
