-- SQL 變更紀錄 (Migration Log)

-- 2026-03-20: 增加群組邀群碼與預算功能
ALTER TABLE groups ADD COLUMN join_code TEXT;
ALTER TABLE groups ADD COLUMN budget INTEGER DEFAULT 0;

-- 2026-03-20: 增加交易描述與地點功能
ALTER TABLE transactions ADD COLUMN description TEXT;
ALTER TABLE transactions ADD COLUMN location TEXT;

-- 2026-03-20: 增加交易類型 'CONTRIBUTION' (預交公費) 支援
-- (不需要變更 Schema，僅在程式邏輯中使用 TransactionType.CONTRIBUTION)

-- 2026-04-15: 增加交易分類功能
ALTER TABLE transactions ADD COLUMN category TEXT DEFAULT 'OTHER';

-- 2026-05-01: 增加個人好友名單功能
CREATE TABLE IF NOT EXISTS friends (
    user_id TEXT,
    friend_id TEXT,
    PRIMARY KEY (user_id, friend_id)
);
