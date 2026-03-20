-- SQL 變更紀錄 (Migration Log)

-- 2026-03-20: 增加群組邀群碼與預算功能
ALTER TABLE groups ADD COLUMN join_code TEXT;
ALTER TABLE groups ADD COLUMN budget INTEGER DEFAULT 0;

-- 2026-03-20: 增加交易描述與地點功能
ALTER TABLE transactions ADD COLUMN description TEXT;
ALTER TABLE transactions ADD COLUMN location TEXT;

-- 2026-03-20: 增加交易類型 'CONTRIBUTION' (預交公費) 支援
-- (不需要變更 Schema，僅在程式邏輯中使用 TransactionType.CONTRIBUTION)
