import customtkinter as ctk
import sys
import os
import json
import threading
import time
import schedule
import uuid
from datetime import datetime
from PIL import Image
import tkinter.filedialog as fd
import tkinter.messagebox as mbox

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.core.main import DebtSystem, TransactionStatus, TransactionType
from frontend.ui.components.common import LoginFrame
from frontend.ui.components.dialogs import JoinGroupDialog, CreateGroupDialog, AddTransactionDialog, QRDialog, AddFriendDialog
from frontend.ui.personal.personal_frame import PersonalFrame
from frontend.ui.group.group_frame import GroupFrame
from frontend.ui.personal.friends_frame import FriendsFrame
from frontend.ui.analysis.analysis_frame import AnalysisFrame
from frontend.ui.analysis.calendar_frame import CalendarFrame

try:
    from pyzbar.pyzbar import decode
    import cv2
    import numpy as np
    SCAN_SUPPORT = True
except ImportError:
    SCAN_SUPPORT = False

CONFIG_PATH = "backend/data/config.json"


class AccountingGUI(ctk.CTk):
    """主程式類別：驅動整個 group ledger 系統的 GUI 核心"""
    def __init__(self):
        super().__init__()
        self.title("group ledger - 多人群組本地記帳系統")
        self.geometry("1150x900")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # 核心數據系統初始化
        self.system = DebtSystem()
        self.current_user = None
        self.current_group_id = None
        self.current_group_name = "未選擇"
        self.current_group_code = "----"
        
        # 主容器配置
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        # 啟動排程執行緒
        self.stop_scheduler = threading.Event()
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        # 檢查自動登入狀態
        self.check_auto_login()

    def run_scheduler(self):
        """背景執行 schedule 任務"""
        schedule.every().day.at("10:00").do(self.background_check)
        while not self.stop_scheduler.is_set():
            schedule.run_pending()
            time.sleep(10)

    def background_check(self):
        """例行性背景檢查 (可擴充發送外部通知邏輯)"""
        if self.current_user:
            overdue = self.system.check_overdue_transactions()
            # 這裡簡單以 Print 示意，實際可實作系統通知
            print(f"Daily Check: Found {len(overdue)} overdue items.")

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
        self.after(1000, self.check_overdue_and_remind)

    def check_overdue_and_remind(self):
        """啟動檢查逾期帳務並彈窗提醒"""
        overdue = self.system.check_overdue_transactions()
        my_overdue = [o for o in overdue if o["user"] == self.current_user]
        if my_overdue:
            msg = "逾期未處理提醒\n\n"
            for o in my_overdue[:5]:
                msg += f"- {o['desc']} (金額: {o['amount']}, 已逾期 {o['days']} 天)\n"
            if len(my_overdue) > 5: msg += "...等更多項目\n"
            msg += "\n請盡速至「我的帳單」或相關群組進行確認與結清。"
            mbox.showwarning("逾期帳務提醒", msg)

    def setup_ui(self):
        """建構主畫面佈局：側邊欄與分頁系統"""
        self.sidebar = ctk.CTkFrame(self.main_container, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        self.user_label = ctk.CTkLabel(self.sidebar, text=f"👤 {self.current_user}", font=ctk.CTkFont(size=16, weight="bold"))
        self.user_label.pack(pady=(30, 5))
        
        self.logout_btn = ctk.CTkButton(self.sidebar, text="登出系統", command=self.logout, 
                                    fg_color="transparent", border_width=1, border_color="#e74c3c", 
                                    text_color="#e74c3c", hover_color="#2c2c2c", height=28)
        self.logout_btn.pack(pady=(0, 25), padx=20)
        
        self.quick_add_btn = ctk.CTkButton(self.sidebar, text="快速記帳 (Quick Add)", 
                                        command=self.open_global_add_tx,
                                        fg_color="#3498db", hover_color="#2980b9", height=45, font=ctk.CTkFont(weight="bold"))
        self.quick_add_btn.pack(pady=15, padx=15, fill="x")
        
        ctk.CTkLabel(self.sidebar, text="選擇群組", font=ctk.CTkFont(size=12)).pack(pady=(10, 0))
        self.group_opt = ctk.CTkOptionMenu(self.sidebar, values=[], command=self.switch_group)
        self.group_opt.set("(尚無群組)")
        self.group_opt.pack(padx=10, pady=5)
        
        ctk.CTkButton(self.sidebar, text="+ 加入群組", command=self.open_join_group).pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(self.sidebar, text="+ 建立新群組", command=self.open_create_group).pack(pady=5, padx=10, fill="x")
        
        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        tab_personal = self.tabview.add("個人中心")
        scroll_p = ctk.CTkScrollableFrame(tab_personal, fg_color="transparent")
        scroll_p.pack(fill="both", expand=True)
        
        self.tab_p = PersonalFrame(scroll_p, self.system, self.current_user)
        self.tab_p.pack(fill="x", pady=(0, 30))
        
        ctk.CTkFrame(scroll_p, height=2, fg_color="#34495e").pack(fill="x", padx=40, pady=10)
        
        self.tab_f = FriendsFrame(scroll_p, self.system, self.current_user)
        self.tab_f.pack(fill="x", pady=30)
        
        ctk.CTkFrame(scroll_p, height=2, fg_color="#34495e").pack(fill="x", padx=40, pady=10)
        
        self.tab_c = CalendarFrame(scroll_p, self.system, self.current_user)
        self.tab_c.pack(fill="x", pady=30)
        
        tab_group = self.tabview.add("群組中心")
        scroll_g = ctk.CTkScrollableFrame(tab_group, fg_color="transparent")
        scroll_g.pack(fill="both", expand=True)
        
        self.tab_g = GroupFrame(scroll_g, self.system)
        self.tab_g.pack(fill="x", pady=(0, 30))
        
        ctk.CTkFrame(scroll_g, height=2, fg_color="#34495e").pack(fill="x", padx=40, pady=10)
        
        self.tab_a = AnalysisFrame(scroll_g, self.system, self.current_user)
        self.tab_a.pack(fill="x", pady=30)

    def load_initial_data(self, target_gid=None):
        """初始數據載入：取得使用者所屬群組並設定首個群組"""
        groups = self.system.get_user_groups(self.current_user)
        if groups:
            g = next((x for x in groups if x["id"] == target_gid), groups[0])
            self.current_group_id, self.current_group_name, self.current_group_code = g["id"], g["name"], g["code"]
        else:
            self.current_group_id = None
            self.current_group_name = "(尚無群組)"
            self.current_group_code = "----"
        self.refresh_ui()

    def refresh_ui(self):
        """刷新全局界面：更新側邊欄群組選單與各分頁內容"""
        groups = self.system.get_user_groups(self.current_user)
        names = [g["name"] for g in groups]
        self.group_opt.configure(values=names)
        
        if names:
            if self.current_group_name in names:
                self.group_opt.set(self.current_group_name)
            else:
                self.group_opt.set(names[0])
        else:
            self.group_opt.set("(尚無群組)")
        
        self.tab_p.refresh()
        self.tab_g.refresh(self.current_group_id, self.current_group_name, self.current_group_code, self.current_user)
        self.tab_f.refresh()
        self.tab_a.refresh(self.current_group_id)
        self.tab_c.refresh(self.current_group_id)

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
        """加入群組成功後的回調處理"""
        if self.system.join_group_by_code(self.current_user, code): 
            mbox.showinfo("成功", f"已成功加入群組碼: {code}")
            self.load_initial_data()
        else:
            mbox.showerror("失敗", "找不到該群組，或是您已在群組中。")

    def open_create_group(self): 
        """開啟建立群組視窗"""
        CreateGroupDialog(self, self.create_group_cb)

    def create_group_cb(self, name):
        """建立群組成功後的回調處理"""
        gid, code = self.system.create_group_with_code(self.current_user, name)
        if gid: 
            mbox.showinfo("群組已建立", f"成功建立群組: {name}\n邀群碼: {code}")
            self.load_initial_data(target_gid=gid)
        else:
            mbox.showerror("錯誤", "建立群組時發生未知錯誤。")

    def open_global_add_tx(self):
        """側邊欄全局快速記帳：直接與當前群組功能綁定"""
        if not self.current_group_id:
            from tkinter import messagebox
            messagebox.showwarning("提示", "請先選擇右上角群組，或進入好友卡片點擊發起私帳！")
            return
        self.open_add_tx()

    def open_add_tx(self, force_participant=None):
        """(原有的) 針對特定群組開啟新增交易對話框"""
        mems = self.system.get_group_members(self.current_group_id)
        AddTransactionDialog(self, mems, self.add_tx_cb, pre_selected=force_participant)

    def add_tx_cb(self, amt, sel, custom, desc, loc, is_private=False, tx_type="EXPENSE", payer=None, date=None):
        """交易對話框提交後的回調"""
        # 使用 UUID 替代純時間戳，避免高頻操作衝突
        tid = f"tx_{uuid.uuid4().hex[:12]}"
        target_gid = "PERSONAL" if is_private else self.current_group_id
        
        if not target_gid: target_gid = "PERSONAL"
        actual_payer = payer if payer else self.current_user

        # 統一處理時間戳：若有指定日期則轉為 datetime 物件並包含當前時刻
        if date:
             try:
                 # date 預期格式為 YYYY-MM-DD
                 d = datetime.strptime(date, "%Y-%m-%d")
                 now = datetime.now()
                 actual_date = d.replace(hour=now.hour, minute=now.minute, second=now.second, microsecond=now.microsecond)
             except Exception:
                 actual_date = datetime.now()
        else:
             actual_date = datetime.now()

        if self.system.propose_transaction(tid, actual_payer, amt, sel, target_gid, custom, tx_type=tx_type, description=desc, location=loc, timestamp=actual_date): 
            self.refresh_ui()

    def confirm_tx(self, tid): 
        """確認交易狀態"""
        self.system.confirm_transaction(self.current_user, tid)
        self.refresh_ui()

    def run_settlement(self, mode="ORIGINAL"):
        """執行結算邏輯"""
        if self.current_group_id:
            if self.system.settle_debts(self.current_group_id, self.current_user, mode=mode): 
                self.refresh_ui()
                mbox.showinfo("結算成功", f"此群組已依照「{mode}」模式完成結算！")

    def show_my_qr(self): 
        """顯示個人 QR Code 名片"""
        QRDialog(self, self.system.generate_qr_path(self.current_user), self.current_user)

    def scan_qr_from_file(self):
        """掃描本地圖片文件以加入好友"""
        if not SCAN_SUPPORT: 
            mbox.showwarning("環境限制", "您的電腦環境缺少 pyzbar 或 opencv 庫，暫無法使用圖片掃描功能。\n請在終端機執行 `pip install pyzbar opencv-python` 以啟用此功能。")
            return
        p = fd.askopenfilename()
        if p:
            img = cv2.imdecode(np.fromfile(p, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            objs = decode(img)
            if objs:
                fid = objs[0].data.decode('utf-8')
                if self.system.add_friend(self.current_user, fid):
                    mbox.showinfo("成功", f"掃描成功！已加入好友：{fid}")
                    self.refresh_ui()
                else: 
                    mbox.showerror("失敗", "無法加入該好友（可能已是好友）。")
            else:
                mbox.showerror("辨識失敗", "無法在該圖片中找到有效的 QR Code。")
                self.refresh_ui()

    def quick_charge(self, fid): 
        """快速向特定好友發起記帳"""
        self.tabview.set("群組中心")
        self.open_add_tx(force_participant=fid)

if __name__ == "__main__":
    app = AccountingGUI()
    app.mainloop()
