import customtkinter as ctk
from PIL import Image

class JoinGroupDialog(ctk.CTkToplevel):
    """加入群組對話框：讓使用者輸入 4 位邀群碼以加入特定群組"""
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("加入群組")
        self.geometry("350x250")
        self.callback = callback
        
        # UI 配置
        ctk.CTkLabel(self, text="輸入 4 位邀群碼", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        self.code_entry = ctk.CTkEntry(self, placeholder_text="A7B2", width=150, height=40)
        self.code_entry.pack(pady=10)
        ctk.CTkButton(self, text="加入", command=self.submit).pack(pady=20)

    def submit(self):
        """提交邀群碼"""
        code = self.code_entry.get().strip().upper()
        if len(code) == 4: 
            self.callback(code)
            self.destroy()

class CreateGroupDialog(ctk.CTkToplevel):
    """建立群組對話框：讓使用者設定群組名稱並生成新群組"""
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("建立新群組")
        self.geometry("350x250")
        self.callback = callback
        
        # UI 配置
        ctk.CTkLabel(self, text="群組名稱", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        self.name_entry = ctk.CTkEntry(self, placeholder_text="合租、旅遊", width=200)
        self.name_entry.pack(pady=10)
        ctk.CTkButton(self, text="建立", command=self.submit).pack(pady=20)

    def submit(self):
        """提交新群組名稱"""
        name = self.name_entry.get().strip()
        if name: 
            self.callback(name)
            self.destroy()

class AddTransactionDialog(ctk.CTkToplevel):
    """新增交易對話框：處理消費金額錄入、參與者選擇與自動分帳邏輯"""
    def __init__(self, parent, members, callback, pre_selected=None):
        super().__init__(parent)
        self.title("記一筆消費")
        self.geometry("450x750")
        self.callback, self.members = callback, members
        self.split_entries, self.check_vars = {}, {}
        
        # 支出內容輸入區
        ctk.CTkLabel(self, text="這筆支出是什麼？", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        self.desc_entry = ctk.CTkEntry(self, placeholder_text="內容"); self.desc_entry.pack(pady=5, padx=40, fill="x")
        self.loc_entry = ctk.CTkEntry(self, placeholder_text="地點"); self.loc_entry.pack(pady=5, padx=40, fill="x")
        self.amount_entry = ctk.CTkEntry(self, placeholder_text="總金額"); self.amount_entry.pack(pady=10, padx=40, fill="x")
        self.amount_entry.bind("<KeyRelease>", self.auto_split)
        
        # 新增模式切換：平均 vs 自訂
        self.mode_var = ctk.StringVar(value="equal")
        self.mode_switch = ctk.CTkSegmentedButton(self, values=["equal", "custom"], 
                                                command=self.toggle_mode, variable=self.mode_var)
        self.mode_switch.configure(values=["平均平分", "手動自訂"])
        self.mode_switch.pack(pady=10)

        self.scroll = ctk.CTkScrollableFrame(self, label_text="分錢的人"); self.scroll.pack(pady=10, padx=20, fill="both", expand=True)
        
        # 動態生成成員勾選清單
        for m in self.members:
            f = ctk.CTkFrame(self.scroll, fg_color="transparent"); f.pack(fill="x", pady=2)
            # 判斷是否預選（如果是好友快速記帳，則預選該好友）
            # parent.current_user 的取得需注意，因為父視窗多層級。
            # 通常傳進來的 parent 是主視窗 (AccountingGUI)
            current_user = getattr(parent, "current_user", "")
            sel = 1 if (not pre_selected or m == pre_selected or m == current_user) else 0
            cv = ctk.IntVar(value=sel); self.check_vars[m] = cv
            ctk.CTkCheckBox(f, text=m, variable=cv, command=self.auto_split).pack(side="left", padx=5)
            ent = ctk.CTkEntry(f, width=80); ent.pack(side="right"); ent.insert(0, "0"); self.split_entries[m] = ent
            
        ctk.CTkButton(self, text="完成並提交", command=self.submit).pack(pady=20)
        self.auto_split()

    def toggle_mode(self, _=None):
        """切換分帳模式時重設欄位狀態"""
        self.auto_split()

    def auto_split(self, _=None):
        """自動計算平分金額邏輯 / 或是解鎖自訂填寫欄位"""
        mode = self.mode_var.get()
        try:
            total = int(self.amount_entry.get() or 0)
            sel = [m for m, v in self.check_vars.items() if v.get() == 1]
            
            if mode == "equal":
                # 平均模式：禁止手動輸入，自動計算且處理餘數
                if not sel: return
                base, rem = total // len(sel), total % len(sel)
                for m, ent in self.split_entries.items():
                    ent.configure(state="normal"); ent.delete(0, "end")
                    if m in sel: 
                        ent.insert(0, str(base + (1 if sel.index(m) < rem else 0)))
                    else: 
                        ent.insert(0, "0")
                    ent.configure(state="readonly")
            else:
                # 自訂模式：解鎖選中的成員欄位供手動填寫
                for m, ent in self.split_entries.items():
                    if self.check_vars[m].get() == 1:
                        ent.configure(state="normal")
                    else:
                        ent.configure(state="normal"); ent.delete(0, "end"); ent.insert(0, "0")
                        ent.configure(state="readonly")
        except: pass

    def submit(self):
        """提交交易數據到主程式：增加總額校驗"""
        try:
            total = int(self.amount_entry.get())
            sel = [m for m, v in self.check_vars.items() if v.get() == 1]
            
            # 收集分帳數據
            custom_splits = {}
            current_sum = 0
            for m in sel:
                amt = int(self.split_entries[m].get() or 0)
                custom_splits[m] = amt
                current_sum += amt
            
            # 校驗總額是否相符
            if current_sum != total:
                from tkinter import messagebox
                messagebox.showerror("金額錯誤", f"分帳總和 ({current_sum}) 與總金額 ({total}) 不符！\n請檢查各人金額。")
                return

            if total > 0 and sel: 
                # 傳遞 custom_splits 給回調
                self.callback(total, sel, custom_splits, self.desc_entry.get(), self.loc_entry.get())
                self.destroy()
        except Exception as e:
            print(f"Submit error: {e}")

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

class TransactionDetailDialog(ctk.CTkToplevel):
    """帳單明細對話框：顯示一筆交易的完整分帳細節與參與者狀態"""
    def __init__(self, parent, tx_details, system=None, current_user=None, refresh_cb=None):
        super().__init__(parent)
        self.title("帳單明細")
        self.geometry("500x650")
        self.details = tx_details
        self.system = system
        self.current_user = current_user
        self.refresh_cb = refresh_cb
        self.setup_ui()

    def setup_ui(self):
        # 標題區 (金額與描述)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=20)
        
        amt_label = ctk.CTkLabel(header, text=f"${self.details['amount']}", font=ctk.CTkFont(size=32, weight="bold"))
        amt_label.pack()
        
        desc = self.details['desc'] or "無描述"
        desc_label = ctk.CTkLabel(header, text=desc, font=ctk.CTkFont(size=16))
        desc_label.pack(pady=5)
        
        # 基礎資訊區 (地點與時間)
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="x", padx=30, pady=10)
        
        loc = self.details['loc'] or "未提供地點"
        ctk.CTkLabel(info_frame, text=f"📍 地點: {loc}").pack(anchor="w", padx=20, pady=5)
        ctk.CTkLabel(info_frame, text=f"📅 時間: {self.details['time']}").pack(anchor="w", padx=20, pady=5)
        ctk.CTkLabel(info_frame, text=f"👤 付款人: {self.details['payer']}").pack(anchor="w", padx=20, pady=5)
        
        # 參與者清單區
        ctk.CTkLabel(self, text="分帳明細", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=40, pady=(20, 5))
        
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=30, pady=10)
        
        for p in self.details['participants']:
            pf = ctk.CTkFrame(scroll, fg_color="transparent")
            pf.pack(fill="x", pady=2)
            
            # 狀態圖示
            status_icon = "✅" if p['status'] == 'CONFIRMED' else "⏳" if p['status'] == 'PENDING' else "💰" if p['status'] == 'SETTLED' else "❌"
            
            ctk.CTkLabel(pf, text=f"{status_icon} {p['user_id']}").pack(side="left", padx=10)
            ctk.CTkLabel(pf, text=f"${p['amount']}").pack(side="right", padx=10)
            
            # 如果是當前使用者 且 尚未結清 且 不是付款人 → 顯示「還款」按鈕
            is_debtor = (p['user_id'] == self.current_user and 
                         p['status'] != 'SETTLED' and 
                         p['user_id'] != self.details['payer'] and
                         p['amount'] > 0)
            if is_debtor and self.system:
                ctk.CTkButton(
                    pf, text="💰 還款", width=80, height=26,
                    fg_color="#e67e22", hover_color="#ca6f1e",
                    command=lambda uid=p['user_id'], amt=p['amount']: self.do_repay(uid, amt)
                ).pack(side="right", padx=5)

        ctk.CTkButton(self, text="關閉", command=self.destroy).pack(pady=20)

    def do_repay(self, debtor_id, amount):
        """執行還款操作"""
        from tkinter import messagebox
        confirm = messagebox.askyesno("確認還款", f"確定向「{self.details['payer']}」還款 ${amount} 嗎？")
        if confirm:
            ok = self.system.repay_transaction(
                self.details['group_id'],
                self.details['id'],
                debtor_id,
                self.details['payer'],
                amount
            )
            if ok:
                messagebox.showinfo("成功", f"還款 ${amount} 已登錄！")
                if self.refresh_cb: self.refresh_cb()
                self.destroy()
            else:
                messagebox.showerror("錯誤", "還款操作失敗，請稍後再試。")
