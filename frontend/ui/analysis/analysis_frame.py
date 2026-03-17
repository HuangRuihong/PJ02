import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("TkAgg")

class AnalysisFrame(ctk.CTkFrame):
    def __init__(self, parent, system, current_user):
        super().__init__(parent, fg_color="transparent")
        self.system = system
        self.current_user = current_user
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(self, text="📊 數據統計與分析", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, columnspan=2, pady=20)
        
        self.chart_container = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_container.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)
        self.chart_container.grid_columnconfigure((0, 1), weight=1)
        self.chart_container.grid_rowconfigure(0, weight=1)

    def refresh(self, group_id=None):
        for w in self.chart_container.winfo_children(): w.destroy()
        
        if not group_id:
            ctk.CTkLabel(self.chart_container, text="請先選擇一個群組進行分析").pack(expand=True)
            return

        txs = self.system.get_group_transactions(group_id)
        if not txs:
            ctk.CTkLabel(self.chart_container, text="目前尚無交易數據").pack(expand=True)
            return

        # 準備數據
        # 1. 開銷佔比 (圓餅圖) - 根據描述或類別 (目前 schema 較簡單，以 payer 代替或金額分佈)
        # 2. 墊付頻率 (長條圖)
        
        payers = {}
        total_by_user = {}
        for tx in txs:
            if tx["type"] == "EXPENSE":
                p = tx["payer"]
                amt = tx["amount"]
                payers[p] = payers.get(p, 0) + 1
                total_by_user[p] = total_by_user.get(p, 0) + amt

        if not total_by_user:
            ctk.CTkLabel(self.chart_container, text="目前尚無支出紀錄").pack(expand=True)
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), dpi=100)
        fig.patch.set_facecolor('#2b2b2b') # CTK dark mode background

        # 圓餅圖：支出金額佔比
        labels = list(total_by_user.keys())
        sizes = list(total_by_user.values())
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, textprops={'color':"w"})
        ax1.set_title("支出金額佔比", color="w")

        # 長條圖：墊付頻率
        users = list(payers.keys())
        counts = list(payers.values())
        ax2.bar(users, counts, color='#3b8ed0')
        ax2.set_title("墊付次數 (頻率)", color="w")
        ax2.set_ylabel("次數", color="w")
        ax2.tick_params(colors='w')

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
