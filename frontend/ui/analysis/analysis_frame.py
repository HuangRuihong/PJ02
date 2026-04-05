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
        
        # 設定整體畫布風格
        plt.rcParams['text.color'] = 'white'
        plt.rcParams['axes.labelcolor'] = 'white'
        plt.rcParams['xtick.color'] = 'white'
        plt.rcParams['ytick.color'] = 'white'
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial'] # 支援中文

        if not group_id:
            self.show_personal_stats()
            return

        self.show_group_stats(group_id)

    def show_personal_stats(self):
        """顯示全域個人消費統計"""
        history = self.system.get_personal_history(self.current_user)
        if not history:
            ctk.CTkLabel(self.chart_container, text="目前尚無任何個人消費紀錄").pack(expand=True)
            return

        # 1. 按群組分類統計
        group_sums = {}
        daily_sums = {}
        for tx in history:
            g_id = tx["group_name"]  # group_name 由 SQL 已處理「個人私帳」對應
            amt = tx["amount"]
            group_sums[g_id] = group_sums.get(g_id, 0) + amt
            
            # 日期趨勢
            date_str = str(tx["timestamp"])[:10]
            daily_sums[date_str] = daily_sums.get(date_str, 0) + amt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), dpi=100)
        fig.patch.set_facecolor('#1a1a1a')

        # 圓餅圖：各群組支出比例
        ax1.pie(group_sums.values(), labels=group_sums.keys(), autopct='%1.1f%%', 
                startangle=140, colors=['#3498db', '#9b59b6', '#2ecc71', '#e67e22', '#f1c40f'])
        ax1.set_title("各群組支出佔比", pad=10)

        # 折線圖：消費趨勢
        sorted_dates = sorted(daily_sums.items())
        dates = [d[0] for d in sorted_dates]
        amts = [d[1] for d in sorted_dates]
        ax2.plot(dates, amts, marker='o', color='#3498db', linewidth=2)
        ax2.set_title("近期消費趨勢")
        ax2.set_ylabel("金額 ($)")
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        ax2.set_facecolor('#1a1a1a')

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        plt.close(fig)  # 釋放 matplotlib 記憶體，避免切換分頁時持續累積
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_group_stats(self, group_id):
        """顯示特定群組內的統計"""
        txs = self.system.get_group_transactions(group_id)
        if not txs:
            ctk.CTkLabel(self.chart_container, text="該群組目前尚無交易數據").pack(expand=True)
            return

        payers = {}
        total_by_user = {}
        for tx in txs:
            if tx["type"] == "EXPENSE":
                p = tx["payer"]
                amt = tx["amount"]
                payers[p] = payers.get(p, 0) + 1
                total_by_user[p] = total_by_user.get(p, 0) + amt

        if not total_by_user:
            ctk.CTkLabel(self.chart_container, text="該群組目前尚無支出紀錄").pack(expand=True)
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), dpi=100)
        fig.patch.set_facecolor('#1a1a1a')

        # 圓餅圖：支出金額佔比
        ax1.pie(total_by_user.values(), labels=total_by_user.keys(), autopct='%1.1f%%', 
                startangle=140, colors=['#1abc9c', '#3498db', '#f1c40f', '#e74c3c'])
        ax1.set_title("群組成員支出佔比", pad=10)

        # 長條圖：墊付頻率
        ax2.bar(payers.keys(), payers.values(), color='#3498db', alpha=0.8)
        ax2.set_title("成員墊付次數")
        ax2.set_ylabel("次數")
        ax2.set_facecolor('#1a1a1a')
        ax2.tick_params(colors='w')

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        plt.close(fig)  # 釋放 matplotlib 記憶體
        canvas.get_tk_widget().pack(fill="both", expand=True)
