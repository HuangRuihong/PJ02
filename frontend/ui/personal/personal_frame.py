import customtkinter as ctk
from datetime import datetime
from ..components.dialogs import TransactionDetailDialog

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
        
        # 將原捲軸容器改為普通容器，由最外層主分頁捲動
        self.main_scroll = ctk.CTkFrame(self, fg_color="transparent")
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
        
        self.dashboard_data = {
            "total_assets": total_assets,
            "receivables": receivables,
            "payables": payables
        }
        
        # 2. 待辦事項 (從應付帳款 payables 中篩出 PENDING 的項目)
        debts, _ = self.system.get_personal_debts(self.current_user)
        self.pending_inbox = []
        for d in debts:
            if d['status'] == 'PENDING':
                # 統一處理日期格式為 YYYY/MM/DD
                raw_date = str(d['date'])
                try:
                    dt = datetime.fromisoformat(raw_date) if " " in raw_date or "T" in raw_date else datetime.strptime(raw_date[:10], '%Y-%m-%d')
                    date_str = dt.strftime('%Y/%m/%d')
                except:
                    date_str = raw_date[:10].replace('-', '/')

                self.pending_inbox.append({
                    "id": d['tx_id'], 
                    "payer": d['creditor'], 
                    "desc": d['desc'] or "一般支出",
                    "amount": d['amount'], 
                    "time": date_str,  # 配合 build_inbox 使用 time 欄位
                    "status": "PENDING",
                    "type": d.get('type'), 
                    "loc": d.get('loc')
                })
                
        # 3. 個人歷史流水紀錄
        try:
            history = self.system.get_personal_history(self.current_user)
            self.history_data = []
            for tx in history:
                is_payer = tx.get('payer_id') == self.current_user
                self.history_data.append({
                    "id": tx['id'], "desc": tx['description'] or "無描述", 
                    "amount": tx['amount'], "date": str(tx['timestamp'])[:10], 
                    "type": "我付錢" if is_payer else "別人付錢"
                })
        except Exception as e:
            print("History Load Error:", e)
            self.history_data = []

    def do_confirm(self, tx_id, tx_type=None, loc_str=None, payer_id=None):
        """處理真實確認交易連動 / 審核結清申請"""
        from tkinter import messagebox
        
        if tx_type == "REPAY_REQUEST":
            tx_ids = loc_str.split(",") if loc_str else []
            if self.system.settle_specific_debts(payer_id, self.current_user, tx_ids):
                # 確認還款請求時，將該請求本身也標記為 SETTLED，以免它變成一筆「新債務」造成金額翻轉
                self.system.confirm_transaction(self.current_user, tx_id, status="SETTLED")
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
        # 1. 先抓取最新資料
        self.load_real_data()
        
        # 2. 清除舊元件後重新繪製各區塊
        for w in self.dashboard_frame.winfo_children(): w.destroy()
        for w in self.inbox_frame.winfo_children(): w.destroy()
        for w in self.history_frame.winfo_children(): w.destroy()
        
        self.build_dashboard()
        self.build_inbox()
        self.build_history()

    def build_dashboard(self):
        """畫出第一區塊：視覺化財務儀表板"""
        ctk.CTkLabel(self.dashboard_frame, text="財務總覽", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        # 使用 load_real_data 已經算好且包含「所有群組+私帳」的真實總額
        total_receivable = self.dashboard_data.get("receivables", 0)
        total_payable = self.dashboard_data.get("payables", 0)
        total_assets = self.dashboard_data.get("total_assets", 0)

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
        
        # 優化：直接使用 load_real_data 預先抓取的資料，避免重複向資料庫發起低效查詢
        pending_items = self.pending_inbox

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

        # 確保排序：最新在最上方 (降序)
        # 有些可能是字串有些是 datetime，統一轉字串比較穩定
        history.sort(key=lambda x: str(x['timestamp']), reverse=True)

        for item in history[:20]: # 僅顯示前 20 筆
            hf = ctk.CTkFrame(self.history_frame, fg_color="transparent")
            hf.pack(fill="x", pady=2)
            hf.grid_columnconfigure(2, weight=1) # 讓描述這欄自動拉伸
            
            # 使用跟隊友一致的 YYYY/MM/DD 格式
            if isinstance(item['timestamp'], str):
                try:
                    dt = datetime.strptime(item['timestamp'][:10], '%Y-%m-%d')
                    date_str = dt.strftime('%Y/%m/%d')
                except:
                    date_str = item['timestamp'][:10].replace('-', '/')
            else:
                date_str = item['timestamp'].strftime('%Y/%m/%d')

            # 1. 日期欄 (固定寬度)
            ctk.CTkLabel(hf, text=date_str, width=100, anchor="w").grid(row=0, column=0, padx=5, sticky="w")
            
            # 2. 群組標籤 (固定寬度)
            g_name = item.get('group_name', '未知群組')
            is_personal = "個人私帳" in g_name
            bg_color = "#34495e" if not is_personal else "#2c3e50"
            group_tag = ctk.CTkLabel(hf, text=g_name, font=ctk.CTkFont(size=11), width=120,
                                    fg_color=bg_color, corner_radius=6, padx=8)
            group_tag.grid(row=0, column=1, padx=5, sticky="w")
            
            # 3. 描述欄 (自動延伸)
            desc_text = item['description'] or '一般支出'
            ctk.CTkLabel(hf, text=f"{desc_text}", anchor="w").grid(row=0, column=2, padx=10, sticky="ew")
            
            # --- 3.5 狀態標籤 (與 GroupFrame 保持一致) ---
            st_color, st_text = self._get_status_info(item.get('status', 'PENDING'))
            status_tag = ctk.CTkLabel(hf, text=st_text, font=ctk.CTkFont(size=10, weight="bold"),
                                    fg_color=st_color, text_color="white", corner_radius=4, width=50)
            status_tag.grid(row=0, column=3, padx=10, sticky="w")
            
            # 4. 金額欄 (固定寬度且靠右)
            is_payer = (item['payer_id'] == self.current_user)
            total_amt = item['amount']
            my_share = item.get('my_share', 0)
            
            amt_info = ctk.CTkFrame(hf, fg_color="transparent", width=220)
            amt_info.grid(row=0, column=3, padx=10, sticky="e")
            
            if is_payer:
                others_owe = total_amt - my_share
                ctk.CTkLabel(amt_info, text=f"總額 ${total_amt} (應收回 ${others_owe})", 
                             text_color="#2ecc71", font=ctk.CTkFont(weight="bold"), anchor="e").pack(anchor="e")
            else:
                ctk.CTkLabel(amt_info, text=f"總額 ${total_amt} (應付 ${my_share})", 
                             text_color="#e74c3c", font=ctk.CTkFont(weight="bold"), anchor="e").pack(anchor="e")

            # ── 整合隊友的：點擊查看明細功能 ──
            click_btn = ctk.CTkButton(hf, text="", fg_color="transparent", hover_color="#2c2c2c", 
                                     command=lambda tid=item['id']: self.show_detail(tid))
            click_btn.place(relx=0, rely=0, relwidth=1, relheight=1)
            # 提升 Label 層級使其顯示在按鈕上
            for child in hf.winfo_children():
                if child != click_btn: child.lift()

    def _get_status_info(self, status):
        """與 GroupFrame 保持一致的狀態資訊"""
        from backend.core.models import TransactionStatus
        mapping = {
            TransactionStatus.PENDING.name: ("#e67e22", "待確認"),
            TransactionStatus.CONFIRMED.name: ("#2ecc71", "已確認"),
            TransactionStatus.SETTLED.name: ("#7f8c8d", "已結清"),
            TransactionStatus.REJECTED.name: ("#e74c3c", "有誤"),
        }
        return mapping.get(status, ("#34495e", status))

    def show_detail(self, tid):
        """顯示交易詳情彈窗 (由隊友實作)"""
        details = self.system.get_transaction_details(tid)
        if details:
            TransactionDetailDialog(
                self.winfo_toplevel(), details,
                system=self.system,
                current_user=self.current_user,
                refresh_cb=self.winfo_toplevel().refresh_ui
            )
