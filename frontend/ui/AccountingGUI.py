import customtkinter as ctk
import sys
import os
import json
from datetime import datetime
from PIL import Image
import tkinter.filedialog as fd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.core.main import DebtSystem, TransactionStatus, TransactionType
from frontend.ui.components.common import LoginFrame
from frontend.ui.components.dialogs import JoinGroupDialog, CreateGroupDialog, AddTransactionDialog, QRDialog
from frontend.ui.personal.personal_frame import PersonalFrame
from frontend.ui.group.group_frame import GroupFrame
from frontend.ui.personal.friends_frame import FriendsFrame

try:
    from pyzbar.pyzbar import decode
    import cv2
    SCAN_SUPPORT = True
except ImportError:
    SCAN_SUPPORT = False

CONFIG_PATH = "backend/data/config.json"



class AccountingGUI(ctk.CTk):
    """主程式類別：驅動整個 Split-it-Smart 系統的 GUI 核心"""
    def __init__(self):
        super().__init__()
        self.title("Split-it-Smart")
        self.geometry("1150x900")
        ctk.set_appearance_mode("dark")
        
        # 核心數據系統初始化
        self.system = DebtSystem()
        self.current_user = None
        self.current_group_id = None
        self.current_group_name = "未選擇"
        self.current_group_code = "----"
        
        # 主容器配置
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        # 檢查自動登入狀態
        self.check_auto_login()

    def check_auto_login(self):
        """啟動時檢查是否存在記住身分的功能"""
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    c = json.load(f)
                    if c.get("remember_me"): 
                        self.login(c["user_id"], True)
                        return
            except: pass
        self.show_login_screen()

    def show_login_screen(self):
        """顯示登入頁面"""
        for w in self.main_container.winfo_children(): w.destroy()
        self.login_p = LoginFrame(self.main_container, self.login)
        self.login_p.pack(fill="both", expand=True)

    def login(self, user, remember):
        """處理登入邏輯"""
        self.current_user = user
        if remember:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w") as f: 
                json.dump({"user_id": user, "remember_me": True}, f)
        self.show_main_app()

    def logout(self):
        """執行登出並清除自動登入設定"""
        if os.path.exists(CONFIG_PATH): os.remove(CONFIG_PATH)
        self.current_user = None
        self.show_login_screen()

    def show_main_app(self):
        """登入後載入主應用程式界面"""
        for w in self.main_container.winfo_children(): w.destroy()
        self.setup_ui()
        self.load_initial_data()

    def setup_ui(self):
        """建構主畫面佈局：側邊欄與分頁系統"""
        # --- 側邊欄 (Sidebar) ---
        self.sidebar = ctk.CTkFrame(self.main_container, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text=f"👤 {self.current_user}", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        ctk.CTkButton(self.sidebar, text="登出系統", command=self.logout, fg_color="transparent").pack(pady=(0, 20))
        
        self.group_opt = ctk.CTkOptionMenu(self.sidebar, values=[], command=self.switch_group)
        self.group_opt.pack(padx=10, pady=5)
        
        ctk.CTkButton(self.sidebar, text="+ 加入群組", command=self.open_join_group).pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(self.sidebar, text="+ 建立新群組", command=self.open_create_group).pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(self.sidebar, text="我的 QR 碼", command=self.show_my_qr, fg_color="transparent", border_width=1).pack(pady=20, padx=10, fill="x")
        
        # --- 主內容區 (Tabs) ---
        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # 初始化三大功能分頁 (採用重構後的目錄結構匯入)
        self.tab_p = PersonalFrame(self.tabview.add("我的帳單"), self.system, self.current_user)
        self.tab_p.pack(fill="both", expand=True)
        
        self.tab_g = GroupFrame(self.tabview.add("群組動態"), self.system)
        self.tab_g.pack(fill="both", expand=True)
        
        self.tab_f = FriendsFrame(self.tabview.add("我的好友"), self.system, self.current_user)
        self.tab_f.pack(fill="both", expand=True)

    def load_initial_data(self, target_gid=None):
        """初始數據載入：取得使用者所屬群組並設定首個群組"""
        groups = self.system.get_user_groups(self.current_user)
        if groups:
            # 優先切換至指定的群組 ID，否則切換至清單第一個
            g = next((x for x in groups if x["id"] == target_gid), groups[0])
            self.current_group_id, self.current_group_name, self.current_group_code = g["id"], g["name"], g["code"]
        else:
            self.current_group_id = None
            self.current_group_name = "沒有任何群組"
            self.current_group_code = "----"
        self.refresh_ui()

    def refresh_ui(self):
        """刷新全局界面：更新側邊欄群組選單與各分頁內容"""
        groups = self.system.get_user_groups(self.current_user)
        self.group_opt.configure(values=[g["name"] for g in groups])
        
        # 分別呼叫各個分頁的 refresh 方法
        self.tab_p.refresh()
        self.tab_g.refresh(self.current_group_id, self.current_group_name, self.current_group_code, self.current_user)
        self.tab_f.refresh()

    def switch_group(self, name):
        """切換目前活動群組"""
        g = next((x for x in self.system.get_user_groups(self.current_user) if x["name"] == name), None)
        if g: 
            self.current_group_id, self.current_group_name, self.current_group_code = g["id"], g["name"], g["code"]
            self.refresh_ui()

    def open_join_group(self): 
        """開啟加入群組視窗"""
        JoinGroupDialog(self, self.join_group_cb)

    def join_group_cb(self, code):
        """加入群組成功後的回調"""
        if self.system.join_group_by_code(self.current_user, code): 
            self.load_initial_data()

    def open_create_group(self): 
        """開啟建立群組視窗"""
        CreateGroupDialog(self, self.create_group_cb)

    def create_group_cb(self, name):
        """建立群組成功後的回調"""
        gid, _ = self.system.create_group_with_code(self.current_user, name)
        if gid: 
            self.load_initial_data(target_gid=gid)

    def open_add_tx(self, force_participant=None):
        """開啟新增交易對話框"""
        mems = self.system.get_group_members(self.current_group_id)
        AddTransactionDialog(self, mems, self.add_tx_cb, pre_selected=force_participant)

    def add_tx_cb(self, amt, sel, custom, desc, loc):
        """交易對話框提交後，呼叫核心系統儲存交易"""
        tid = f"tx_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if self.system.propose_transaction(tid, self.current_user, amt, sel, self.current_group_id, custom, description=desc, location=loc): 
            self.refresh_ui()

    def confirm_tx(self, tid): 
        """確認交易"""
        self.system.confirm_transaction(self.current_user, tid)
        self.refresh_ui()

    def run_settlement(self):
        """(待開發項目) 執行結算邏輯"""
        sel = [tid for tid, (v, _) in self.payable_vars.items() if v.get()]
        if sel and self.system.settle_debts(self.current_user, self.payable_vars[sel[0]][1], sel): 
            self.refresh_ui()

    def show_my_qr(self): 
        """顯示個人 QR Code 名片"""
        QRDialog(self, self.system.generate_qr_path(self.current_user), self.current_user)

    def scan_qr_from_file(self):
        """掃描本地圖片文件以加入好友"""
        if not SCAN_SUPPORT: return
        p = fd.askopenfilename()
        if p:
            objs = decode(cv2.imread(p))
            if objs and self.system.add_friend(self.current_user, objs[0].data.decode('utf-8')): 
                self.refresh_ui()

    def quick_charge(self, fid): 
        """快速向特定好友發起記帳"""
        self.tabview.set("群組動態")
        self.open_add_tx(force_participant=fid)

if __name__ == "__main__":
    # 啟動應用程式
    app = AccountingGUI()
    app.mainloop()
