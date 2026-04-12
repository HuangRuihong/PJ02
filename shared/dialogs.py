import customtkinter as ctk
from PIL import Image
from datetime import datetime
from tkcalendar import DateEntry

class JoinGroupDialog(ctk.CTkToplevel):
    """加入群組對話框：讓使用者輸入 4 位邀群碼以加入特定群組"""
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("加入群組")
        self.geometry("350x250")
        self.callback = callback
        self.attributes("-topmost", True)
        self.grab_set() # 模態視窗使背景無法點擊
        self.after(10, self.lift)
        self.focus_force()
        
        # UI 配置
        ctk.CTkLabel(self, text="輸入 6 位邀群碼", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        self.code_entry = ctk.CTkEntry(self, placeholder_text="A7B2C9", width=150, height=40)
        self.code_entry.pack(pady=10)
        ctk.CTkButton(self, text="加入", command=self.submit).pack(pady=20)

    def submit(self):
        """提交邀群碼"""
        code = self.code_entry.get().strip().upper()
        if len(code) == 6: 
            self.callback(code)
            self.destroy()
        else:
            from tkinter import messagebox
            messagebox.showerror("格式錯誤", "請輸入完整的 6 位數邀群碼！")

class CreateGroupDialog(ctk.CTkToplevel):
    """建立群組對話框：讓使用者設定群組名稱並生成新群組"""
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("建立新群組")
        self.geometry("350x250")
        self.callback = callback
        self.attributes("-topmost", True)
        self.grab_set()
        self.after(10, self.lift)
        self.focus_force()
        
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

class AddFriendDialog(ctk.CTkToplevel):
    """加入好友對話框：提供 ID 輸入與 QR Code 掃描兩大功能"""
    def __init__(self, parent, add_cb, scan_cb):
        super().__init__(parent)
        self.title("加入好友")
        self.geometry("380x320")
        self.add_cb = add_cb
        self.scan_cb = scan_cb
        self.attributes("-topmost", True)
        self.grab_set()
        self.after(10, self.lift)
        self.focus_force()
        
        # UI 配置
        ctk.CTkLabel(self, text="[+] 加入新好友", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))
        
        # 1. ID 輸入區
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(pady=10, padx=40, fill="x")
        
        ctk.CTkLabel(input_frame, text="請輸入好友 ID:", font=ctk.CTkFont(size=13)).pack(anchor="w")
        self.id_entry = ctk.CTkEntry(input_frame, placeholder_text="例如: user_abc", height=35)
        self.id_entry.pack(fill="x", pady=(5, 0))
        
        # 2. 功能按鈕區
        btns_frame = ctk.CTkFrame(self, fg_color="transparent")
        btns_frame.pack(pady=20, padx=40, fill="x")
        
        self.confirm_btn = ctk.CTkButton(btns_frame, text="確認加入", height=40, 
                                        fg_color="#2ecc71", hover_color="#27ae60",
                                        command=self.submit_id)
        self.confirm_btn.pack(fill="x", pady=5)
        
        ctk.CTkLabel(btns_frame, text="--- 或者 ---", text_color="gray").pack(pady=5)
        
        self.scan_btn = ctk.CTkButton(btns_frame, text="[掃描] 掃描名片圖片", height=40, 
                                     fg_color="#34495e", hover_color="#2c3e50",
                                     command=self.trigger_scan)
        self.scan_btn.pack(fill="x", pady=5)

    def submit_id(self):
        """提交手動輸入的 ID"""
        fid = self.id_entry.get().strip()
        if fid:
            self.add_cb(fid)
            self.destroy()
        else:
            from tkinter import messagebox
            messagebox.showwarning("格式錯誤", "請輸入有效的好友 ID！")

    def trigger_scan(self):
        """觸發主程式的 QR Code 掃描功能"""
        self.scan_cb()
        self.destroy()

class AddTransactionDialog(ctk.CTkToplevel):
    """新增交易對話框：處理消費金額錄入、參與者選擇與自動分帳邏輯"""

    # 使用中文字串作為內部模式識別 key，避免 CTkSegmentedButton 的 variable 與 values 不一致問題
    MODE_EQUAL        = "平均分帳"
    MODE_CUSTOM       = "手動自訂"
    MODE_PRIVATE      = "個人私帳"

    def __init__(self, parent, members, callback, pre_selected=None, initial_data=None):
        super().__init__(parent)
        self.title("記一筆消費")
        self.geometry("450x780")
        self.callback, self.members = callback, members
        self.split_entries, self.check_vars, self.check_boxes = {}, {}, {}
        self.current_user = getattr(parent, "current_user", "")
        self.attributes("-topmost", True)
        self.grab_set()
        self.after(10, self.lift)
        self.focus_force()

        # ── 標題 ──────────────────────────────────────────
        ctk.CTkLabel(self, text="記一筆消費", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 5))

        # ── 付款人 ────────────────────────────────────────
        payer_frame = ctk.CTkFrame(self, fg_color="transparent")
        payer_frame.pack(fill="x", padx=40, pady=5)
        ctk.CTkLabel(payer_frame, text="誰付的錢？").pack(side="left", padx=5)
        self.payer_var = ctk.StringVar(value=self.current_user)
        self.payer_opt = ctk.CTkOptionMenu(payer_frame, values=self.members, variable=self.payer_var)
        self.payer_opt.pack(side="right", fill="x", expand=True)

        # ── 描述 & 金額 ───────────────────────────────────
        self.desc_entry = ctk.CTkEntry(self, placeholder_text="這筆支出是什麼？ (如: 飯店住宿)")
        self.desc_entry.pack(pady=8, padx=40, fill="x")

        self.amt_entry = ctk.CTkEntry(self, placeholder_text="0", width=180, height=40, font=ctk.CTkFont(size=18, weight="bold"))
        self.amt_entry.pack(pady=5)
        self.amt_entry.bind("<KeyRelease>", lambda e: self.auto_split())

        # --- 日期選擇 (New: 統一為 YYYY/MM/DD) ---
        date_frame = ctk.CTkFrame(self, fg_color="transparent")
        date_frame.pack(pady=5)
        ctk.CTkLabel(date_frame, text="日期:").pack(side="left", padx=5)
        
        # 使用 DateEntry 替代 ctk.CTkEntry，提供實體日曆選擇
        self.date_entry = DateEntry(
            date_frame, width=12, background='#1f538d', 
            foreground='white', borderwidth=2, 
            date_pattern='yyyy/mm/dd',
            headersbackground='#2c3e50', headersforeground='white',
            selectbackground='#3498db', state='readonly'
        )
        self.date_entry.pack(side="left", padx=5)

        # ── 進階選項（預設展開）──────────────────────────
        self.show_extra = True
        self.extra_btn = ctk.CTkButton(
            self, text="^ 隱藏進階選項",
            fg_color="transparent", text_color="gray", hover_color="#2c2c2c",
            command=self.toggle_extra
        )
        self.extra_btn.pack(pady=(8, 0))

        self.extra_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.extra_frame.pack(fill="x")  # 預設展開

        self.loc_entry = ctk.CTkEntry(self.extra_frame, placeholder_text="地點 (選填)")
        self.loc_entry.pack(pady=5, padx=40, fill="x")

        # 分帳模式切換（直接使用中文作為 variable 值）
        self.mode_var = ctk.StringVar(value=self.MODE_EQUAL)
        self.mode_switch = ctk.CTkSegmentedButton(
            self.extra_frame,
            values=[self.MODE_EQUAL, self.MODE_CUSTOM, self.MODE_PRIVATE],
            command=self.toggle_mode,
            variable=self.mode_var
        )
        self.mode_switch.pack(pady=8, padx=20, fill="x")

        # 模式說明文字
        self.mode_hint = ctk.CTkLabel(self.extra_frame, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self.mode_hint.pack()

        # ── 即時分配狀態 Label ────────────────────────────
        self.balance_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.balance_label.pack(pady=(5, 0))

        # ── 成員勾選清單 ───────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(self, label_text="分帳成員")
        self.scroll.pack(pady=5, padx=20, fill="both", expand=True)

        for m in self.members:
            f = ctk.CTkFrame(self.scroll, fg_color="transparent")
            f.pack(fill="x", pady=2)
            sel = 1 if (not pre_selected or m == pre_selected or m == self.current_user) else 0
            cv = ctk.IntVar(value=sel)
            self.check_vars[m] = cv
            cb = ctk.CTkCheckBox(f, text=m, variable=cv, command=self.auto_split)
            cb.pack(side="left", padx=5)
            self.check_boxes[m] = cb
            ent = ctk.CTkEntry(f, width=80)
            ent.pack(side="right")
            ent.insert(0, "0")
            self.split_entries[m] = ent

        # ── 提交按鈕 ───────────────────────────────────────
        self.submit_btn = ctk.CTkButton(
            self, text="儲存變更" if initial_data else "(o) 確認提交並生成帳項",
            command=self.submit,
            fg_color="#2ecc71", hover_color="#27ae60",
            height=45, font=ctk.CTkFont(weight="bold")
        )
        self.submit_btn.pack(pady=15, padx=40, fill="x")
        
        self.initial_data = initial_data
        if self.initial_data:
            self.load_initial_data()
        else:
            self.auto_split()

    def load_initial_data(self):
        """用於編輯模式：載入原本的資料並設為自訂模式以確保金額精確一致"""
        self.title("編輯帳單")
        self.payer_var.set(self.initial_data.get('payer', self.current_user))
        if self.initial_data.get('desc'):
            self.desc_entry.insert(0, self.initial_data.get('desc'))
        self.amt_entry.insert(0, str(self.initial_data.get('amount', 0)))
        
        if self.initial_data.get('loc'):
            if not self.show_extra: self.toggle_extra()
            self.loc_entry.insert(0, self.initial_data.get('loc'))
            
        raw_ts = self.initial_data.get('time')
        if raw_ts:
            try:
                from datetime import datetime
                if isinstance(raw_ts, str):
                    d = datetime.fromisoformat(raw_ts) if ":" in raw_ts else datetime.strptime(raw_ts[:10], "%Y-%m-%d")
                else: d = raw_ts
                self.date_entry.set_date(d.date())
            except: pass

        self.mode_var.set(self.MODE_PRIVATE if self.initial_data.get('group_id') == 'PERSONAL' else self.MODE_CUSTOM)
        if self.mode_var.get() == self.MODE_CUSTOM and not self.show_extra:
            self.toggle_extra()

        for m, cb in self.check_vars.items():
            cb.set(0)
            self.split_entries[m].configure(state="normal")
            self.split_entries[m].delete(0, "end")
            self.split_entries[m].insert(0, "0")

        for p in self.initial_data.get('participants', []):
            uid = p['user_id']
            if uid in self.check_vars:
                self.check_vars[uid].set(1)
                self.split_entries[uid].configure(state="normal")
                self.split_entries[uid].delete(0, "end")
                self.split_entries[uid].insert(0, str(p['amount']))
        
        self.auto_split()

    def toggle_extra(self):
        """切換顯示/隱藏進階選項"""
        if self.show_extra:
            self.extra_frame.pack_forget()
            self.extra_btn.configure(text="v 更多選項 (地點/模式)")
        else:
            self.extra_frame.pack(after=self.extra_btn, fill="x")
            self.extra_btn.configure(text="^ 隱藏進階選項")
        self.show_extra = not self.show_extra

    def toggle_mode(self, _=None):
        """切換分帳模式時更新提示文字、重綁 CheckBox command，並重算"""
        mode = self.mode_var.get()
        hints = {
            self.MODE_EQUAL:        "自動依人數均分，餘數分配給排序靠前的成員。",
            self.MODE_CUSTOM:       "勾選參與者後，手動輸入各人應付金額。",
            self.MODE_PRIVATE:      "僅記錄於個人帳單，不計入群組分帳。",
        }
        self.mode_hint.configure(text=hints.get(mode, ""))
        for m, cb in self.check_boxes.items():
            cb.configure(command=self.auto_split)
        self.auto_split()

    def auto_split(self, _=None):
        """根據模式自動計算分帳金額，並更新即時餘額提示"""
        mode = self.mode_var.get()
        try:
            total = int(self.amt_entry.get() or 0)

            if mode == self.MODE_PRIVATE:
                # 私帳模式：運作邏輯與「平均分帳」相同，但會被標記為私有的
                self.scroll.configure(label_text="私帳成員 (不計入群組公帳)")
            else:
                self.scroll.configure(label_text="分帳成員")

            sel = [m for m, v in self.check_vars.items() if v.get() == 1]

            if mode in [self.MODE_EQUAL, self.MODE_PRIVATE]:
                if not sel:
                    self._update_balance_label(total, 0)
                    return
                base, rem = total // len(sel), total % len(sel)
                for m, ent in self.split_entries.items():
                    ent.configure(state="normal")
                    ent.delete(0, "end")
                    if m in sel:
                        ent.insert(0, str(base + (1 if sel.index(m) < rem else 0)))
                    else:
                        ent.insert(0, "0")
                    ent.configure(state="readonly")
                self._update_balance_label(total, total)

            else:  # MODE_CUSTOM
                for m, ent in self.split_entries.items():
                    if self.check_vars[m].get() == 1:
                        ent.configure(state="normal")
                    else:
                        ent.configure(state="normal")
                        ent.delete(0, "end")
                        ent.insert(0, "0")
                        ent.configure(state="readonly")
                current_sum = sum(int(self.split_entries[m].get() or 0) for m in sel)
                self._update_balance_label(total, current_sum)
        except:
            pass

    def _update_balance_label(self, total, assigned):
        """更新即時分配狀態 Label"""
        diff = total - assigned
        if total == 0:
            self.balance_label.configure(text="", text_color="gray")
        elif diff == 0:
            self.balance_label.configure(text=f"[已全額分配]：${total}", text_color="#2ecc71")
        elif diff > 0:
            self.balance_label.configure(text=f"尚有 ${diff} 未分配（已分 ${assigned} / 總額 ${total}）", text_color="#e67e22")
        else:
            self.balance_label.configure(text=f"超出分配 ${abs(diff)}（已分 ${assigned} / 總額 ${total}）", text_color="#e74c3c")

    def submit(self):
        """提交交易數據到主程式"""
        try:
            total_str = self.amt_entry.get().strip()
            if not total_str:
                from tkinter import messagebox
                messagebox.showerror("金額錯誤", "請輸入有效的金額！")
                return
            total = int(total_str)
            mode  = self.mode_var.get()
            payer = self.payer_var.get()
            desc  = self.desc_entry.get()
            loc   = self.loc_entry.get().strip()
            # 獲取日期物件 (DateEntry.get_date() 直接回傳 datetime.date)
            try:
                dt_obj = self.date_entry.get_date()
                final_date = dt_obj.strftime("%Y-%m-%d")
            except Exception:
                from tkinter import messagebox
                messagebox.showerror("日期錯誤", "無法讀取所選日期，請重新選擇。")
                return

            # ── 提交邏輯 ───────────────────────
            is_private = (mode == self.MODE_PRIVATE)
            sel = [m for m, v in self.check_vars.items() if v.get() == 1]
            if not sel:
                from tkinter import messagebox
                messagebox.showerror("未選成員", "請至少勾選一位分帳成員。")
                return

            custom_splits = {m: int(self.split_entries[m].get() or 0) for m in sel}
            current_sum   = sum(custom_splits.values())

            if current_sum != total:
                from tkinter import messagebox
                messagebox.showerror("金額錯誤", f"分帳總和（${current_sum}）與總金額（${total}）不符！")
                return

            if total > 0 and sel:
                self.callback(total, sel, custom_splits, desc, loc, is_private=is_private, payer=payer, date=final_date)
                self.destroy()
            else:
                from tkinter import messagebox
                messagebox.showerror("提交失敗", "請確保金額大於 0 且包含至少一位成員。")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("格式錯誤", "請檢查金額輸入是否正確！")

class QRDialog(ctk.CTkToplevel):
    """我的 QR 名片對話框"""
    def __init__(self, parent, qr_path, uid):
        super().__init__(parent)
        self.title("我的 QR Code 名片")
        self.geometry("400x550")
        self.attributes("-topmost", True)
        self.grab_set()
        self.after(10, self.lift)
        self.focus_force()
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
        self.attributes("-topmost", True)
        self.grab_set()
        self.after(10, self.lift)
        self.focus_force()
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
        ctk.CTkLabel(info_frame, text=f" [地點]: {loc}").pack(anchor="w", padx=20, pady=5)
        
        # 格式化顯示時間
        raw_time = self.details['time']
        if isinstance(raw_time, str):
            display_time = raw_time[:10].replace('-', '/')
        else:
            display_time = raw_time.strftime('%Y/%m/%d')
        ctk.CTkLabel(info_frame, text=f" [日期]: {display_time}").pack(anchor="w", padx=20, pady=5)
        ctk.CTkLabel(info_frame, text=f" 付款人: {self.details['payer']}").pack(anchor="w", padx=20, pady=5)
        
        # 參與者清單區
        ctk.CTkLabel(self, text="分帳明細", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=40, pady=(20, 5))
        
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=30, pady=10)
        
        for p in self.details['participants']:
            pf = ctk.CTkFrame(scroll, fg_color="transparent")
            pf.pack(fill="x", pady=2)
            
            # 狀態文字替代圖示
            status_map = {'CONFIRMED': '(已確認)', 'PENDING': '(待處理)', 'SETTLED': '(已結清)', 'REJECTED': '(有誤)'}
            status_text = status_map.get(p['status'], f"({p['status']})")
            
            ctk.CTkLabel(pf, text=f"{status_text} {p['user_id']}").pack(side="left", padx=10)
            ctk.CTkLabel(pf, text=f"${p['amount']}").pack(side="right", padx=10)
            
            # 如果是當前使用者 且 尚未結清 且 不是付款人 → 顯示「還款」按鈕
            is_debtor = (p['user_id'] == self.current_user and 
                         p['status'] != 'SETTLED' and 
                         p['user_id'] != self.details['payer'] and
                         p['amount'] > 0)
            if is_debtor and self.system:
                ctk.CTkButton(
                    pf, text="還款", width=80, height=26,
                    fg_color="#e67e22", hover_color="#ca6f1e",
                    command=lambda uid=p['user_id'], amt=p['amount']: self.do_repay(uid, amt)
                ).pack(side="right", padx=5)

        # 底部按鈕區
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="關閉", command=self.destroy, width=100).pack(side="left", padx=10)
        
        # 僅付款人可刪除交易 (防呆)
        if self.current_user == self.details['payer']:
            ctk.CTkButton(
                btn_frame, text="[刪除] 刪除交易", 
                fg_color="#e74c3c", hover_color="#c0392b",
                command=self.do_delete, width=100
            ).pack(side="left", padx=10)

    def do_delete(self):
        """執行刪除交易操作"""
        from tkinter import messagebox
        confirm = messagebox.askyesno("確認刪除", "確定要刪除這筆交易嗎？此操作無法恢復。")
        if confirm:
            if self.system.delete_transaction(self.details['id']):
                messagebox.showinfo("成功", "交易已刪除！")
                if self.refresh_cb: self.refresh_cb()
                self.destroy()
            else:
                messagebox.showerror("錯誤", "刪除失敗，請檢查資料庫狀態。")

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

class BudgetDialog(ctk.CTkToplevel):
    """預算設定對話框：讓使用者輸入群組的總預算"""
    def __init__(self, parent, current_budget, callback):
        super().__init__(parent)
        self.title("設定群組預算")
        self.geometry("350x250")
        self.callback = callback
        self.attributes("-topmost", True)
        self.grab_set()
        self.after(10, self.lift)
        self.focus_force()
        
        ctk.CTkLabel(self, text="設定本次旅遊/活動總預算", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        self.budget_entry = ctk.CTkEntry(self, placeholder_text="輸入總預算金額 (如: 50000)", width=200)
        self.budget_entry.insert(0, str(current_budget) if current_budget > 0 else "")
        self.budget_entry.pack(pady=10)
        
        ctk.CTkButton(self, text="儲存預算", command=self.submit, fg_color="#2ecc71").pack(pady=20)

    def submit(self):
        try:
            val = int(self.budget_entry.get().strip() or 0)
            self.callback(val)
            self.destroy()
        except ValueError:
            from tkinter import messagebox
            messagebox.showerror("格式錯誤", "請輸入有效的數字金額！")
