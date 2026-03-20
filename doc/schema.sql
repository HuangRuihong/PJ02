-- 債務系統資料庫結構 (Debt System Database Schema)

-- 群組表
CREATE TABLE IF NOT EXISTS groups (
    group_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    join_code TEXT,
    budget INTEGER DEFAULT 0
);

-- 使用者與群組關聯表
CREATE TABLE IF NOT EXISTS group_members (
    group_id TEXT,
    user_id TEXT,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES groups(group_id)
);

-- 交易主表
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    group_id TEXT,
    payer_id TEXT,
    amount INTEGER, -- 以元儲存 (TWD)
    status TEXT, -- PENDING, CONFIRMED, REJECTED, SETTLED
    type TEXT DEFAULT 'EXPENSE', -- EXPENSE, SETTLEMENT, CONTRIBUTION
    description TEXT,
    location TEXT,
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

-- 好友表
CREATE TABLE IF NOT EXISTS friends (
    user_id TEXT,
    friend_id TEXT,
    PRIMARY KEY (user_id, friend_id)
);
