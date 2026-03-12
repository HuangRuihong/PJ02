import customtkinter as ctk
from frontend.ui.components.dialogs import TransactionDetailDialog



class GroupFrame(ctk.CTkFrame):
    def __init__(self, parent, system):
        super().__init__(parent, fg_color="transparent")
        self.system = system
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
        
        self.refresh_btn = ctk.CTkButton(self.header, text="🔄 刷新", command=self.handle_refresh, fg_color="#3498db", hover_color="#2980b9")
        self.refresh_btn.grid(row=0, column=2, sticky="ew", padx=4)
        
        self.settle_btn = ctk.CTkButton(self.header, text="💰 一鍵結算", command=self.handle_settle, fg_color="#2ecc71", hover_color="#27ae60")
        self.settle_btn.grid(row=0, column=3, sticky="ew", padx=4)
        
        self.delete_btn = ctk.CTkButton(self.header, text="🗑️ 刪除群組", command=self.handle_delete, fg_color="#e74c3c", hover_color="#c0392b")
        self.delete_btn.grid(row=0, column=4, sticky="ew", padx=4)

        # 成員名單顯示區
        self.members_info = ctk.CTkFrame(self, fg_color="transparent")
        self.members_info.pack(fill="x", padx=30)
        self.members_label = ctk.CTkLabel(self.members_info, text="成員: 加載中...", font=ctk.CTkFont(size=13), text_color="gray")
        self.members_label.pack(side="left")
        
        self.scroll = ctk.CTkScrollableFrame(self, label_text="最近活動")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

    def refresh(self, gid, gname, gcode, current_user):
        self.gid, self.current_user = gid, current_user
        
        # 處理無群組顯示邏輯
        if not gid:
            self.info_label.configure(text="❌ 目前沒有任何群組")
            self.members_info.pack_forget()
            self.settle_btn.grid_remove()
            self.delete_btn.grid_remove()
            self.add_btn.grid_remove()
            self.refresh_btn.grid_remove()
            for w in self.scroll.winfo_children(): w.destroy()
            return
        
        # 有群組時恢復顯示按鈕與資訊
        self.info_label.configure(text=f"👥 {gname} (代碼: {gcode})")
        
        # 為確保佈局順序正確 (標題 -> 成員 -> 活動捲動區)，先暫時移開捲動區再重新放入
        self.scroll.pack_forget()
        self.members_info.pack(fill="x", padx=30, pady=(0, 5))
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 恢復按鈕 (使用 grid 與 setup_ui 保持一致)
        self.add_btn.grid(row=0, column=1, sticky="ew", padx=4)
        self.refresh_btn.grid(row=0, column=2, sticky="ew", padx=4)
        self.settle_btn.grid(row=0, column=3, sticky="ew", padx=4)
        self.delete_btn.grid(row=0, column=4, sticky="ew", padx=4)
        
        # 載入並顯示成員名單
        members = self.system.get_group_members(gid)
        self.members_label.configure(text=f"成員: {', '.join(members)}")
        
        for w in self.scroll.winfo_children(): w.destroy()
        
        txs = self.system.get_group_transactions(gid)
        for tx in txs:
            f = ctk.CTkFrame(self.scroll); f.pack(fill="x", pady=5)
            # 根據交易類型顯示不同的前綴文字
            prefix = "💰 償還了" if tx['type'] == 'SETTLEMENT' else "💸 支出"
            l = ctk.CTkLabel(f, text=f"{tx['payer']} {prefix} {tx['amount']}")
            l.pack(side="left", padx=10)
            
            # 綁定雙擊事件 (框架與內部標籤皆綁定，提升操作靈敏度)
            f.bind("<Double-1>", lambda e, tid=tx['id']: self.show_details(tid))
            l.bind("<Double-1>", lambda e, tid=tx['id']: self.show_details(tid))
            
            if current_user in tx['pending_confirmations']:
                ctk.CTkButton(f, text="確認", width=60, command=lambda tid=tx['id']: self.winfo_toplevel().confirm_tx(tid)).pack(side="right", padx=5)

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

    def handle_settle(self):
        """處理結算按鈕點擊"""
        plan = self.system.settle_debts(self.gid, self.current_user)
        if not plan:
            # 彈出提示：沒有可結算的項目
            from tkinter import messagebox
            messagebox.showinfo("結算結果", "目前沒有已確認且未結算的交易項目。")
            return
            
        # 顯示結算計畫結果
        result_str = "\n".join([f"· {p['from']} 應給 {p['to']} ${p['amount']}" for p in plan])
        from tkinter import messagebox
        messagebox.showinfo("結算與還款落實", f"經過抵銷計算，建議還款方式如下：\n\n{result_str}\n\n✅ 上述還款紀錄已正式登錄於系統活動紀錄中。\n所有相關支出已標記為已結清。")
        self.winfo_toplevel().refresh_ui()

    def handle_delete(self):
        """處理刪除群組按鈕點擊：實作二次確認"""
        from tkinter import messagebox
        confirm = messagebox.askyesno("確認刪除", f"確定要徹底刪除群組「{self.winfo_toplevel().current_group_name}」嗎？\n\n這將會抹除該群組內所有的交易紀錄與參與者資料，且無法復原。")
        
        if confirm:
            if self.system.delete_group(self.gid):
                messagebox.showinfo("成功", "群組已成功移除。")
                # 強制主視窗重新載入群組數據（會切換到剩餘的第一個群組）
                self.winfo_toplevel().load_initial_data()
            else:
                messagebox.showerror("錯誤", "刪除群組時發生錯誤。")
