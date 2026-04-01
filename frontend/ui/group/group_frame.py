import customtkinter as ctk
from frontend.ui.components.dialogs import TransactionDetailDialog, BudgetDialog



class GroupFrame(ctk.CTkFrame):
    def __init__(self, parent, system):
        super().__init__(parent, fg_color="transparent")
        self.system = system
        self.budget_val = 0  # 預先初始化避免 AttributeError
        self.setup_ui()

    def setup_ui(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=20, pady=10)
        
        # 設定 grid 欄位：label 固定，按鈕欄均分彈性空間
        self.header.columnconfigure(0, weight=0)  # label (固定)
        for col in range(1, 6):
            self.header.columnconfigure(col, weight=1)  # 按鈕欄 (自適應)
        
        self.info_label = ctk.CTkLabel(self.header, text="群組動態", font=ctk.CTkFont(size=20, weight="bold"))
        self.info_label.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        self.add_btn = ctk.CTkButton(self.header, text="+ 記一筆", command=self.open_add_tx)
        self.add_btn.grid(row=0, column=1, sticky="ew", padx=4)
        
        self.refresh_btn = ctk.CTkButton(self.header, text="刷新", command=self.handle_refresh, fg_color="#3498db", hover_color="#2980b9")
        self.refresh_btn.grid(row=0, column=2, sticky="ew", padx=4)
        
        self.settle_btn = ctk.CTkButton(self.header, text="一鍵結算", command=self.handle_settle, fg_color="#2ecc71", hover_color="#27ae60")
        self.settle_btn.grid(row=0, column=3, sticky="ew", padx=4)
        
        self.export_btn = ctk.CTkButton(self.header, text="匯出帳單", command=self.handle_export_bill, fg_color="#f39c12", hover_color="#e67e22")
        self.export_btn.grid(row=0, column=4, sticky="ew", padx=4)
        
        self.delete_btn = ctk.CTkButton(self.header, text="刪除群組", command=self.handle_delete, fg_color="#e74c3c", hover_color="#c0392b")
        self.delete_btn.grid(row=0, column=5, sticky="ew", padx=4)

        # 成員名單顯示區
        self.members_info = ctk.CTkFrame(self, fg_color="transparent")
        self.members_info.pack(fill="x", padx=30)
        self.members_label = ctk.CTkLabel(self.members_info, text="成員: 加載中...", font=ctk.CTkFont(size=13), text_color="gray")
        self.members_label.pack(side="left")
        
        ctk.CTkLabel(self, text="最近活動", font=ctk.CTkFont(size=14, weight="bold"), text_color="gray").pack(padx=20, pady=(10,0), anchor="w")
        self.scroll = ctk.CTkFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # 預算卡片：改為在頂部資訊區 pack，避免遮擋長清單
        self.budget_card = ctk.CTkFrame(self, fg_color="#2c3e50", corner_radius=10, border_width=1, border_color="#34495e")
        self.budget_card.pack(fill="x", padx=20, pady=5)
        
        self.budget_label = ctk.CTkLabel(self.budget_card, text="預算: 加載中...", font=ctk.CTkFont(size=14, weight="bold"), text_color="#2ecc71")
        self.budget_label.pack(side="left", padx=15, pady=8)
        
        # 綁定點擊事件以設定預算
        self.budget_card.bind("<Button-1>", lambda e: self.open_set_budget())
        self.budget_label.bind("<Button-1>", lambda e: self.open_set_budget())

    def refresh(self, gid, gname, gcode, current_user):
        self.gid, self.current_user = gid, current_user
        
        # 處理無群組顯示邏輯
        if not gid:
            self.info_label.configure(text="(尚無群組)")
            self.members_info.pack_forget()
            self.settle_btn.grid_remove()
            self.delete_btn.grid_remove()
            self.add_btn.grid_remove()
            self.refresh_btn.grid_remove()
            self.budget_card.place_forget()
            for w in self.scroll.winfo_children(): w.destroy()
            return
        
        # 有群組時恢復顯示按鈕與資訊
        self.info_label.configure(text=f"{gname} (代碼: {gcode})")
        
        # 為確保佈局順序正確 (標題 -> 成員 -> 活動捲動區)，先暫時移開捲動區再重新放入
        self.scroll.pack_forget()
        self.members_info.pack(fill="x", padx=30, pady=(0, 5))
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 恢復按鈕 (使用 grid 與 setup_ui 保持一致)
        self.add_btn.grid(row=0, column=1, sticky="ew", padx=4)
        self.refresh_btn.grid(row=0, column=2, sticky="ew", padx=4)
        self.settle_btn.grid(row=0, column=3, sticky="ew", padx=4)
        self.export_btn.grid(row=0, column=4, sticky="ew", padx=4)
        self.delete_btn.grid(row=0, column=5, sticky="ew", padx=4)
        
        # 載入並顯示成員名單
        members = self.system.get_group_members(gid)
        self.members_label.configure(text=f"成員: {', '.join(members)}")
        
        # 載入並刷新預算資訊
        budget_info = self.system.get_group_budget_status(gid)
        self.budget_val = budget_info["budget"]
        # 使用者要求格式：預算：$XX,XXX元 (僅顯示剩餘預算數字)
        self.budget_label.configure(text=f"預算: ${budget_info['remaining']:,}元")
        
        for w in self.scroll.winfo_children(): w.destroy()
        
        txs = self.system.get_group_transactions(gid)
        for tx in txs:
            f = ctk.CTkFrame(self.scroll); f.pack(fill="x", pady=5)
            
            # --- 左側：狀態標籤 ---
            st_color, st_text = self._get_status_info(tx['status'])
            status_tag = ctk.CTkLabel(f, text=st_text, font=ctk.CTkFont(size=10, weight="bold"),
                                    fg_color=st_color, text_color="white", corner_radius=4, width=60)
            status_tag.pack(side="left", padx=(10, 5), pady=5)

            # --- 中間：交易描述 ---
            prefix = "償還了" if tx['type'] == 'SETTLEMENT' else "支出"
            l = ctk.CTkLabel(f, text=f"{tx['payer']} {prefix} ${tx['amount']:,} - {tx['description'] or ''}")
            l.pack(side="left", padx=10)
            
            # 綁定雙擊事件
            f.bind("<Double-1>", lambda e, tid=tx['id']: self.show_details(tid))
            l.bind("<Double-1>", lambda e, tid=tx['id']: self.show_details(tid))
            status_tag.bind("<Double-1>", lambda e, tid=tx['id']: self.show_details(tid))
            
            if current_user in tx['pending_confirmations']:
                btn_text = "確認收錢" if tx['type'] == 'SETTLEMENT' else "確認"
                ctk.CTkButton(f, text=btn_text, width=80, command=lambda tid=tx['id']: self.winfo_toplevel().confirm_tx(tid)).pack(side="right", padx=5)
            
            # 只有付款人可以看到「催帳」按鈕來提醒他人
            # 只有付款人可以看到提醒按鈕
            if current_user == tx['payer'] and tx['pending_confirmations']:
                remind_text = "提醒確認" if tx['type'] == 'SETTLEMENT' else "催帳"
                ctk.CTkButton(f, text=remind_text, width=80, fg_color="#d35400", hover_color="#a04000",
                             command=lambda tid=tx['id']: self.handle_notify(tid)).pack(side="right", padx=5)

    def open_add_tx(self):
        self.winfo_toplevel().open_add_tx()

    def handle_refresh(self):
        """手動刷新介面：重新查詢群組清單，可偵測到他人刪除群組的變化"""
        self.winfo_toplevel().load_initial_data(target_gid=self.gid)

    def show_details(self, tid):
        """顯示交易明細彈窗（含欠款人還款按鈕）"""
        details = self.system.get_transaction_details(tid)
        if details:
            TransactionDetailDialog(
                self.winfo_toplevel(), details,
                system=self.system,
                current_user=self.current_user,
                refresh_cb=self.winfo_toplevel().refresh_ui
            )

    def handle_notify(self, tid):
        """處理催帳按鈕：顯示通知文字並提供複製"""
        from tkinter import messagebox
        import pyperclip
        msg = self.system.get_notification_message(tid)
        if messagebox.askyesno("生成催帳訊息", f"已生成針對該筆交易的提醒文字：\n\n{msg}\n\n是否將此文字複製到剪貼簿？", parent=self.winfo_toplevel()):
            try:
                pyperclip.copy(msg)
                messagebox.showinfo("成功", "催帳訊息已複製到剪貼簿，您可以直接貼上至 Line 或其他通訊軟體。", parent=self.winfo_toplevel())
            except Exception:
                messagebox.showerror("錯誤", "無法存取剪貼簿。", parent=self.winfo_toplevel())

    def handle_export_bill(self):
        """匯出群組帳單摘要"""
        from tkinter import messagebox
        import pyperclip
        summary = self.system.generate_group_bill_summary(self.gid)
        if messagebox.askyesno("匯出帳單摘要", f"即將生成的帳單內容如下：\n\n{summary}\n\n是否將此摘要複製到剪貼簿？", parent=self.winfo_toplevel()):
            try:
                pyperclip.copy(summary)
                messagebox.showinfo("成功", "帳單摘要已複製到剪貼簿。", parent=self.winfo_toplevel())
            except Exception:
                messagebox.showerror("錯誤", "無法存取剪貼簿。", parent=self.winfo_toplevel())

    def handle_settle(self):
        """處理結算按鈕點擊：詢問模式"""
        from tkinter import messagebox
        # 詢問結算模式
        mode_choice = messagebox.askquestion("選擇結算模式", 
            "請選擇結算模式：\n\n"
            "是 (Yes): 逐筆結清 (直接給付)\n"
            "否 (No): 智慧自動抵銷 (最省事)\n"
            "取消: 中止結算", icon='question', type='yesnocancel', parent=self.winfo_toplevel())
        
        if mode_choice == 'cancel': return
        
        mode = "ORIGINAL" if mode_choice == 'yes' else "SIMPLIFIED"
        
        plan = self.system.settle_debts(self.gid, self.current_user, mode=mode)
        if not plan:
            messagebox.showinfo("結算結果", "目前沒有已確認且未結算的交易項目。", parent=self.winfo_toplevel())
            return
            
        # 顯示結算計畫結果
        result_str = "\n".join([f"· {p['from']} 應給 {p['to']} ${p['amount']}" for p in plan])
        messagebox.showinfo("結算與還款落實", 
            f"已使用「{mode}」模式完成計算，建議還款方式如下：\n\n{result_str}\n\n"
            "上述還款紀錄已正式登錄於系統活動紀錄中。\n所有相關支出已標記為已結清。", parent=self.winfo_toplevel())
        self.winfo_toplevel().refresh_ui()

    def handle_delete(self):
        """處理刪除群組按鈕點擊：實作二次確認"""
        from tkinter import messagebox
        confirm = messagebox.askyesno("確認刪除", f"確定要徹底刪除群組「{self.winfo_toplevel().current_group_name}」嗎？\n\n這將會抹除該群組內所有的交易紀錄與參與者資料，且無法復原。", parent=self.winfo_toplevel())
        
        if confirm:
            if self.system.delete_group(self.gid):
                messagebox.showinfo("成功", "群組已成功移除。", parent=self.winfo_toplevel())
                # 強制主視窗重新載入群組數據（會切換到剩餘的第一個群組）
                self.winfo_toplevel().load_initial_data()
            else:
                messagebox.showerror("錯誤", "刪除群組時發生錯誤。", parent=self.winfo_toplevel())

    def open_set_budget(self):
        """開啟預算設定對話框"""
        BudgetDialog(self.winfo_toplevel(), self.budget_val, self.save_budget_cb)

    def _get_status_info(self, status):
        """根據狀態回傳顏色與顯示文字"""
        from backend.core.main import TransactionStatus
        mapping = {
            TransactionStatus.PENDING.name: ("#e67e22", "待確認"),
            TransactionStatus.CONFIRMED.name: ("#2ecc71", "已確認"),
            TransactionStatus.SETTLED.name: ("#7f8c8d", "已結清"),
            TransactionStatus.REJECTED.name: ("#e74c3c", "有誤"),
        }
        return mapping.get(status, ("#34495e", status))

    def save_budget_cb(self, amount):
        """儲存預算後的回調"""
        if self.system.set_group_budget(self.gid, amount):
            self.refresh(self.gid, self.winfo_toplevel().current_group_name, self.winfo_toplevel().current_group_code, self.current_user)
        else:
            from tkinter import messagebox
            messagebox.showerror("錯誤", "無法存取資料庫設定預算。", parent=self.winfo_toplevel())
