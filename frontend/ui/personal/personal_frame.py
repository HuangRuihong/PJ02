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
        self.title_label = ctk.CTkLabel(self.main_scroll, text=f"👤 {self.current_user} 的個人帳單儀表板", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(10, 20), anchor="w", padx=20)
        
        # 準備三個主要區塊的容器
        self.dashboard_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.dashboard_frame.pack(fill="x", padx=10, pady=10)
        
        self.inbox_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.inbox_frame.pack(fill="x", padx=10, pady=10)
        
        self.history_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.history_frame.pack(fill="x", padx=10, pady=10)

    def load_mock_data(self):
        """
        這裡全部使用【假資料 (Mock Data)】。
        因為這段程式碼非常簡單直觀，未來等隊友把後端寫好後，
        你只要把這些變數換成 self.system.get_XXX() 就能直接串接！
        """
        # 1. 財務總覽 (總餘額)
        self.mock_dashboard = {
            "total_assets": 850,     # 總淨資產
            "receivables": 1200,     # 別人欠我的總額 (應收)
            "payables": 350          # 我欠別人的總額 (應付)
        }
        
        # 2. 待辦事項 / 通知匣 (完全對應企劃書的【非同步驗證機制】)
        # status="Pending" 代表這是一筆還沒被正式寫進帳本的款項，需要你的驗證
        self.mock_pending_inbox = [
            {"id": "tx_01", "payer": "室友A", "desc": "幫忙代購好市多衛生紙", "amount": 75, "date": "2023-11-01", "status": "Pending"},
            {"id": "tx_02", "payer": "室友B", "desc": "昨晚叫的宵夜披薩", "amount": 200, "date": "2023-11-02", "status": "Pending"}
        ]
        
        # 3. 個人最新的詳細帳務 (對應月度結算)
        self.mock_history = [
            {"id": "tx_03", "desc": "繳水電費", "amount": 500, "date": "2023-10-25", "type": "我付錢"},
            {"id": "tx_04", "desc": "買公用垃圾袋", "amount": 120, "date": "2023-10-20", "type": "別人付錢"}
        ]

    def refresh(self):
        """刷新畫面，每次點擊到這個「我的帳單」分頁時都會呼叫"""
        
        # 1. 載入我們寫好的假資料
        self.load_mock_data()
        
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
        ctk.CTkLabel(self.dashboard_frame, text="📊 財務總覽", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        # 建立一個橫向排列的容器放三個卡片
        cards_container = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        cards_container.pack(fill="x", pady=5)
        # 讓三個卡片寬度平均分配
        cards_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        # --- 卡片1：應收 (別人欠我錢) ---
        card1 = ctk.CTkFrame(cards_container, fg_color="#2c3e50")
        card1.grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkLabel(card1, text="別人欠我 (應收)", text_color="gray80").pack(pady=(10, 0))
        ctk.CTkLabel(card1, text=f"+ ${self.mock_dashboard['receivables']}", 
                     font=ctk.CTkFont(size=24, weight="bold"), text_color="#2ecc71").pack(pady=(5, 15))
                     
        # --- 卡片2：應付 (我欠別人錢) ---
        card2 = ctk.CTkFrame(cards_container, fg_color="#2c3e50")
        card2.grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkLabel(card2, text="我欠別人 (應付)", text_color="gray80").pack(pady=(10, 0))
        ctk.CTkLabel(card2, text=f"- ${self.mock_dashboard['payables']}", 
                     font=ctk.CTkFont(size=24, weight="bold"), text_color="#e74c3c").pack(pady=(5, 15))

        # --- 卡片3：個人淨資產 ---
        card3 = ctk.CTkFrame(cards_container, fg_color="#1f538d")
        card3.grid(row=0, column=2, padx=5, sticky="ew")
        ctk.CTkLabel(card3, text="個人淨資產", text_color="gray90").pack(pady=(10, 0))
        ctk.CTkLabel(card3, text=f"= ${self.mock_dashboard['total_assets']}", 
                     font=ctk.CTkFont(size=24, weight="bold"), text_color="white").pack(pady=(5, 15))

    def build_inbox(self):
        """畫出第二區塊：待確認的通知匣 (Pending Inbox)"""
        ctk.CTkLabel(self.inbox_frame, text="📥 待辦事項 (需要你驗證的帳款)", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(20, 10))
        
        if not self.mock_pending_inbox:
            # 如果沒有待辦事項，顯示灰色提示
            ctk.CTkLabel(self.inbox_frame, text="目前沒有需要驗證的帳款喔！", text_color="gray").pack(pady=10)
            return
            
        for item in self.mock_pending_inbox:
            # 設計一個帶有橘色邊框的代辦事項卡片
            item_card = ctk.CTkFrame(self.inbox_frame, border_width=1, border_color="#e67e22")
            item_card.pack(fill="x", pady=5)
            
            # --- 卡片內的左邊區域：文字描述 ---
            left_info = ctk.CTkFrame(item_card, fg_color="transparent")
            left_info.pack(side="left", fill="both", expand=True, padx=15, pady=10)
            
            ctk.CTkLabel(left_info, text=f"發起人: {item['payer']}  |  日期: {item['date']}", 
                         font=ctk.CTkFont(size=12), text_color="gray70").pack(anchor="w")
            ctk.CTkLabel(left_info, text=f"{item['desc']} (向你請款: ${item['amount']})", 
                         font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(5, 0))
            
            # --- 卡片內的右邊區域：確認與拒絕按鈕 ---
            right_btns = ctk.CTkFrame(item_card, fg_color="transparent")
            right_btns.pack(side="right", padx=15, pady=10)
            
            # 點擊按鈕的假動作 (目前只會在終端機印出字，方便你點擊測試)
            btn_ok = ctk.CTkButton(right_btns, text="✅ 確認", width=60, fg_color="#27ae60", hover_color="#2ecc71",
                                   command=lambda tx=item['id']: print(f"[系統提示] 你點擊了確認帳款: {tx}"))
            btn_ok.pack(side="left", padx=5)
            
            btn_no = ctk.CTkButton(right_btns, text="❌ 有誤", width=60, fg_color="#c0392b", hover_color="#e74c3c",
                                   command=lambda tx=item['id']: print(f"[系統提示] 你拒絕了帳款: {tx}"))
            btn_no.pack(side="left", padx=5)

    def build_history(self):
        """畫出第三區塊：歷史紀錄清單"""
        ctk.CTkLabel(self.history_frame, text="📜 最近的帳務紀錄", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(20, 10))
        
        for item in self.mock_history:
            hf = ctk.CTkFrame(self.history_frame, fg_color="transparent")
            hf.pack(fill="x", pady=2)
            
            # 左側：時間與描述
            ctk.CTkLabel(hf, text=f"{item['date']}").pack(side="left", padx=10)
            ctk.CTkLabel(hf, text=f"{item['desc']}", width=150, anchor="w").pack(side="left", padx=10)
            
            # 右側：錢的顏色。如果是「別人的帳，我必須付錢」就標紅，反之標綠。
            color = "#e74c3c" if item['type'] == "別人付錢" else "#2ecc71"
            prefix = "-" if item['type'] == "別人付錢" else "+"
            
            ctk.CTkLabel(hf, text=item['type'], text_color="gray60", width=80, anchor="e").pack(side="right", padx=10)
            ctk.CTkLabel(hf, text=f"{prefix}${item['amount']}", text_color=color, font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10)
