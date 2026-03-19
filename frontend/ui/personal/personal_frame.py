import customtkinter as ctk

class PersonalFrame(ctk.CTkFrame):
    def __init__(self, parent, system, current_user):
        """
        初始化個人介面
        parent: 上層容器
        system: 隊友寫的後端核心
        current_user: 當前登入的使用者名字
        """
        super().__init__(parent, fg_color="transparent")
        self.system = system
        self.current_user = current_user
        
        # 建立大捲軸容器，讓畫面滿了可以往下滾
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 標題
        self.title_label = ctk.CTkLabel(self.main_scroll, text=f"{self.current_user} 的個人帳單儀表板", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(10, 20), anchor="w", padx=20)
        
        # 準備三個主要區塊的容器
        self.dashboard_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.dashboard_frame.pack(fill="x", padx=10, pady=10)
        
        self.inbox_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.inbox_frame.pack(fill="x", padx=10, pady=10)
        
        self.history_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.history_frame.pack(fill="x", padx=10, pady=10)

    def load_real_data(self):
        """直接從後端資料庫取得真實數據"""
        # 1. 財務總覽計算
        summary = self.system.get_user_summary(self.current_user) # dict {friend: balance}
        total_assets = sum(summary.values())
        receivables = sum(val for val in summary.values() if val > 0)
        payables = sum(abs(val) for val in summary.values() if val < 0)
        
        self.mock_dashboard = {
            "total_assets": total_assets,
            "receivables": receivables,
            "payables": payables
        }
        
        # 2. 待辦事項 (從應付帳款 payables 中篩出 PENDING 的項目)
        debts, _ = self.system.get_personal_debts(self.current_user)
        self.mock_pending_inbox = []
        for d in debts:
            if d['status'] == 'PENDING':
                self.mock_pending_inbox.append({
                    "id": d['tx_id'], "payer": d['creditor'], "desc": d['desc'],
                    "amount": d['amount'], "date": str(d['date'])[:10], "status": "Pending",
                    "type": d.get('type'), "loc": d.get('loc')
                })
                
        # 3. 個人歷史流水紀錄
        try:
            history = self.system.get_personal_history(self.current_user)
            self.mock_history = []
            for tx in history:
                is_payer = tx.get('payer') == self.current_user
                self.mock_history.append({
                    "id": tx['id'], "desc": tx['desc'] or "無描述", 
                    "amount": tx['amount'], "date": str(tx['time'])[:10], 
                    "type": "我付錢" if is_payer else "別人付錢"
                })
        except Exception as e:
            print("History Load Error:", e)
            self.mock_history = []

    def do_confirm(self, tx_id, tx_type=None, loc_str=None, payer_id=None):
        """處理真實確認交易連動 / 審核結清申請"""
        from tkinter import messagebox
        
        if tx_type == "REPAY_REQUEST":
            tx_ids = loc_str.split(",") if loc_str else []
            if self.system.settle_specific_debts(payer_id, self.current_user, tx_ids):
                self.system.confirm_transaction(self.current_user, tx_id)
                messagebox.showinfo("成功", "✅ 已確認收到款項，相關債務已正式銷帳！")
                self.winfo_toplevel().refresh_ui()
            else:
                messagebox.showerror("錯誤", "結清處理失敗！")
        else:
            if self.system.confirm_transaction(self.current_user, tx_id):
                messagebox.showinfo("成功", "✅ 已確認此筆帳款，正式納入結算！")
                self.winfo_toplevel().refresh_ui()

    def do_reject(self, tx_id, tx_type=None):
        """處理拒絕交易邏輯"""
        from tkinter import messagebox
        if hasattr(self.system, "reject_transaction") and self.system.reject_transaction(self.current_user, tx_id):
            action_name = "還款回報" if tx_type == "REPAY_REQUEST" else "帳款"
            messagebox.showinfo("拒絕", f"❌ 已退回這筆{action_name}。")
            self.winfo_toplevel().refresh_ui()
        else:
            messagebox.showinfo("拒絕", "❌ 已拒絕此筆帳款。(目前後端尚未實作退件機制，僅為前端展示)")

    def refresh(self):
        """刷新畫面，每次點擊到這個「我的帳單」分頁時都會呼叫"""
        
        # 1. 載入真實庫資料
        self.load_real_data()
        
        # 2. 為了避免重複疊加畫面，畫新介面前先把舊的元件刪掉
        for w in self.dashboard_frame.winfo_children(): w.destroy()
        for w in self.inbox_frame.winfo_children(): w.destroy()
        for w in self.history_frame.winfo_children(): w.destroy()
        
        # 3. 呼叫三個方法來把自己負責的區塊畫上去
        self.build_dashboard()
        self.build_inbox()
        self.build_history()

    def build_dashboard(self):
        """畫出第一區塊：視覺化財務儀表板"""
        ctk.CTkLabel(self.dashboard_frame, text="財務總覽", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        # 從實體系統獲取真實餘額
        balances = self.system.get_group_balances("PERSONAL") # 個人私帳餘額
        # 這裡需要一個能統合個人所有債務的方法，目前暫以個別服務獲取
        # 為了簡化，我們可以在 DebtSystem 增加一個統合餘額方法
        # 在此暫時從後端計算所有群組的總合
        total_receivable = 0
        total_payable = 0
        
        groups = self.system.get_user_groups(self.current_user)
        for g in groups:
            gb = self.system.get_group_balances(g['id'])
            my_bal = gb.get(self.current_user, 0)
            if my_bal > 0: total_receivable += my_bal
            else: total_payable += abs(my_bal)

        total_assets = total_receivable - total_payable

        # 建立一個橫向排列的容器放三個卡片
        cards_container = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        cards_container.pack(fill="x", pady=5)
        cards_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        # --- 卡片1：應收 (別人欠我錢) ---
        card1 = ctk.CTkFrame(cards_container, fg_color="#2c3e50")
        card1.grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkLabel(card1, text="別人欠我 (應收)", text_color="gray80").pack(pady=(10, 0))
        ctk.CTkLabel(card1, text=f"+ ${total_receivable}", 
                     font=ctk.CTkFont(size=24, weight="bold"), text_color="#2ecc71").pack(pady=(5, 15))
                     
        # --- 卡片2：應付 (我欠別人錢) ---
        card2 = ctk.CTkFrame(cards_container, fg_color="#2c3e50")
        card2.grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkLabel(card2, text="我欠別人 (應付)", text_color="gray80").pack(pady=(10, 0))
        ctk.CTkLabel(card2, text=f"- ${total_payable}", 
                     font=ctk.CTkFont(size=24, weight="bold"), text_color="#e74c3c").pack(pady=(5, 15))

        # --- 卡片3：個人淨資產 ---
        card3 = ctk.CTkFrame(cards_container, fg_color="#1f538d")
        card3.grid(row=0, column=2, padx=5, sticky="ew")
        ctk.CTkLabel(card3, text="個人淨資產", text_color="gray90").pack(pady=(10, 0))
        ctk.CTkLabel(card3, text=f"= ${total_assets}", 
                     font=ctk.CTkFont(size=24, weight="bold"), text_color="white").pack(pady=(5, 15))

    def build_inbox(self):
        """畫出第二區塊：待確認的通知匣 (Pending Inbox)"""
        ctk.CTkLabel(self.inbox_frame, text="待辦事項 (需要你驗證的帳款)", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(20, 10))
        
        # 從真實後端獲取待確認交易
        # 我們掃描所有群組與私帳中，當前使用者狀態為 PENDING 的項目
        pending_items = []
        groups = self.system.get_user_groups(self.current_user)
        target_gids = [g['id'] for g in groups] + ["PERSONAL"]
        
        for gid in target_gids:
            txs = self.system.get_group_transactions(gid)
            for tx in txs:
                if self.current_user in tx['pending_confirmations']:
                    pending_items.append(tx)

        if not pending_items:
            ctk.CTkLabel(self.inbox_frame, text="目前沒有需要驗證的帳款喔！", text_color="gray").pack(pady=10)
            return
            
        for item in pending_items:
            item_card = ctk.CTkFrame(self.inbox_frame, border_width=1, border_color="#e67e22")
            item_card.pack(fill="x", pady=5)
            
            left_info = ctk.CTkFrame(item_card, fg_color="transparent")
            left_info.pack(side="left", fill="both", expand=True, padx=15, pady=10)
            
            ctk.CTkLabel(left_info, text=f"發起人: {item['payer']}  |  日期: {item['time']}", 
                         font=ctk.CTkFont(size=12), text_color="gray70").pack(anchor="w")
            if item.get("type") == "REPAY_REQUEST":
                title_text = f"{item['desc']} (回報還款: ${item['amount']})"
            else:
                title_text = f"{item['desc']} (向你請款: ${item['amount']})"
                
            ctk.CTkLabel(left_info, text=title_text, 
                         font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(5, 0))
            
            right_btns = ctk.CTkFrame(item_card, fg_color="transparent")
            right_btns.pack(side="right", padx=15, pady=10)
            
            # 綁定真實的確認與拒絕動作
            btn_ok = ctk.CTkButton(right_btns, text="✅ 確認", width=60, fg_color="#27ae60", hover_color="#2ecc71",
                                   command=lambda tx=item['id'], t=item.get("type"), loc=item.get("loc"), p=item["payer"]: self.do_confirm(tx, t, loc, p))
            btn_ok.pack(side="left", padx=5)
            
            btn_no = ctk.CTkButton(right_btns, text="❌ 有誤", width=60, fg_color="#c0392b", hover_color="#e74c3c",
                                   command=lambda tx=item['id'], t=item.get("type"): self.do_reject(tx, t))
            btn_no.pack(side="left", padx=5)

    def build_history(self):
        """畫出第三區塊：歷史紀錄清單"""
        ctk.CTkLabel(self.history_frame, text="最近的帳務紀錄", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(20, 10))
        
        # 獲取真實歷史紀錄 (包含個人私帳)
        history = self.system.get_personal_history(self.current_user)
        if not history:
            ctk.CTkLabel(self.history_frame, text="尚無任何歷史紀錄。", text_color="gray").pack(pady=10)
            return

        for item in history[:20]: # 僅顯示前 20 筆
            hf = ctk.CTkFrame(self.history_frame, fg_color="transparent")
            hf.pack(fill="x", pady=2)
            
            # 左側：時間與描述
            date_str = item['timestamp'][:10] if isinstance(item['timestamp'], str) else item['timestamp'].strftime('%Y-%m-%d')
            ctk.CTkLabel(hf, text=date_str).pack(side="left", padx=10)
            ctk.CTkLabel(hf, text=f"{item['description'] or '一般支出'}", width=150, anchor="w").pack(side="left", padx=10)
            
            # 右側：金額。如果是「我付錢」就標綠，如果是「我被分帳」就標紅。
            # 這裡的邏輯需要配合 get_personal_history 的回傳值
            is_payer = (item['payer_id'] == self.current_user)
            color = "#2ecc71" if is_payer else "#e74c3c"
            prefix = "+" if is_payer else "-"
            label_text = "我付錢" if is_payer else "被分帳"
            
            ctk.CTkLabel(hf, text=label_text, text_color="gray60", width=80, anchor="e").pack(side="right", padx=10)
            ctk.CTkLabel(hf, text=f"{prefix}${item['amount']}", text_color=color, font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10)
