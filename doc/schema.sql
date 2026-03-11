-- 債務系統資料庫結構 (Debt System Database Schema)

-- 群組表
CREATE TABLE IF NOT EXISTS groups (
    group_id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

-- 使用者與群組關聯表
CREATE TABLE IF NOT EXISTS group_members (
    group_id TEXT,
    user_id TEXT,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES groups(group_id)
);

-- 交易標題表
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    group_id TEXT,
    payer_id TEXT,
    amount INTEGER, -- 以元儲存 (TWD)
    status TEXT, -- PENDING, CONFIRMED, SETTLED
    type TEXT DEFAULT 'EXPENSE', -- EXPENSE, SETTLEMENT
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(group_id)
);

-- 交易參與者與狀態表 (參與者層級狀態機)
CREATE TABLE IF NOT EXISTS transaction_participants (
    transaction_id TEXT,
    user_id TEXT,
    owed_amount INTEGER,
    status TEXT DEFAULT 'PENDING', -- PENDING, CONFIRMED, REJECTED, SETTLED
    settled_at DATETIME,
    PRIMARY KEY (transaction_id, user_id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
);
