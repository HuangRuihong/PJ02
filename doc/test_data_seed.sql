-- 3 天 4 人測試開銷種子資料 (Test Data Seed for 3 Days and 4 People)
-- 群組: test_group_001 (測試旅遊群組)
-- 使用者: 87, 88, 89, 90

-- 1. 建立測試群組
INSERT OR IGNORE INTO groups (group_id, name, join_code, budget) VALUES ('test_group_001', '測試旅遊群組', 'TEST66', 30000);

-- 2. 建立群組成員
INSERT OR IGNORE INTO group_members (group_id, user_id) VALUES ('test_group_001', '87');
INSERT OR IGNORE INTO group_members (group_id, user_id) VALUES ('test_group_001', '88');
INSERT OR IGNORE INTO group_members (group_id, user_id) VALUES ('test_group_001', '89');
INSERT OR IGNORE INTO group_members (group_id, user_id) VALUES ('test_group_001', '90');

-- 3. 插入交易紀錄 (Day 1: 2026-04-10)
-- 項目: 高鐵票, 支付者: 87, 金額: 4800, 全員均分
INSERT INTO transactions (transaction_id, group_id, payer_id, amount, status, type, description, timestamp) 
VALUES ('tx_d1_01', 'test_group_001', '87', 4800, 'CONFIRMED', 'EXPENSE', '高鐵票 (台北-左營)', '2026-04-10 10:30:00');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d1_01', '87', 1200, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d1_01', '88', 1200, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d1_01', '89', 1200, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d1_01', '90', 1200, 'CONFIRMED');

-- 項目: 租車費用, 支付者: 88, 金額: 2500, 全員均分
INSERT INTO transactions (transaction_id, group_id, payer_id, amount, status, type, description, timestamp) 
VALUES ('tx_d1_02', 'test_group_001', '88', 2500, 'CONFIRMED', 'EXPENSE', '租車費用 (3天)', '2026-04-10 14:00:00');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d1_02', '87', 625, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d1_02', '88', 625, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d1_02', '89', 625, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d1_02', '90', 625, 'CONFIRMED');

-- 項目: 晚餐, 支付者: 89, 金額: 1800, 全員均分
INSERT INTO transactions (transaction_id, group_id, payer_id, amount, status, type, description, timestamp) 
VALUES ('tx_d1_03', 'test_group_001', '89', 1800, 'CONFIRMED', 'EXPENSE', '第一天晚餐 (熱炒)', '2026-04-10 19:30:00');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d1_03', '87', 450, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d1_03', '88', 450, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d1_03', '89', 450, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d1_03', '90', 450, 'CONFIRMED');

-- 4. 插入交易紀錄 (Day 2: 2026-04-11)
-- 項目: 景點門票, 支付者: 87, 金額: 1200, 全員均分
INSERT INTO transactions (transaction_id, group_id, payer_id, amount, status, type, description, timestamp) 
VALUES ('tx_d2_01', 'test_group_001', '87', 1200, 'CONFIRMED', 'EXPENSE', '園區門票 (300*4)', '2026-04-11 11:00:00');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d2_01', '87', 300, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d2_01', '88', 300, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d2_01', '89', 300, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d2_01', '90', 300, 'CONFIRMED');

-- 項目: 下午茶, 支付者: 89, 金額: 600, 87,88,89 均分 (90未參與)
INSERT INTO transactions (transaction_id, group_id, payer_id, amount, status, type, description, timestamp) 
VALUES ('tx_d2_02', 'test_group_001', '89', 600, 'CONFIRMED', 'EXPENSE', '下午茶 (咖啡廳)', '2026-04-11 15:30:00');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d2_02', '87', 200, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d2_02', '88', 200, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d2_02', '89', 200, 'CONFIRMED');

-- 項目: 晚餐, 支付者: 90, 金額: 1000, 全員均分
INSERT INTO transactions (transaction_id, group_id, payer_id, amount, status, type, description, timestamp) 
VALUES ('tx_d2_03', 'test_group_001', '90', 1000, 'PENDING', 'EXPENSE', '夜市大合集', '2026-04-11 20:00:00');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d2_03', '87', 250, 'PENDING');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d2_03', '88', 250, 'PENDING');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d2_03', '89', 250, 'PENDING');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d2_03', '90', 250, 'CONFIRMED');

-- 5. 插入交易紀錄 (Day 3: 2026-04-12)
-- 項目: 伴手禮, 支付者: 88, 金額: 2000, 88,89 均分 (代買)
INSERT INTO transactions (transaction_id, group_id, payer_id, amount, status, type, description, timestamp) 
VALUES ('tx_d3_01', 'test_group_001', '88', 2000, 'CONFIRMED', 'EXPENSE', '當地特產 (代買)', '2026-04-12 10:00:00');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d3_01', '88', 1000, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d3_01', '89', 1000, 'CONFIRMED');

-- 項目: 午餐, 支付者: 89, 金額: 1600, 全員均分
INSERT INTO transactions (transaction_id, group_id, payer_id, amount, status, type, description, timestamp) 
VALUES ('tx_d3_02', 'test_group_001', '89', 1600, 'CONFIRMED', 'EXPENSE', '回程午餐', '2026-04-12 13:00:00');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d3_02', '87', 400, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d3_02', '88', 400, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d3_02', '89', 400, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d3_02', '90', 400, 'CONFIRMED');

-- 項目: 油資, 支付者: 90, 金額: 800, 全員均分
INSERT INTO transactions (transaction_id, group_id, payer_id, amount, status, type, description, timestamp) 
VALUES ('tx_d3_03', 'test_group_001', '90', 800, 'CONFIRMED', 'EXPENSE', '還車加油', '2026-04-12 15:30:00');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d3_03', '87', 200, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d3_03', '88', 200, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d3_03', '89', 200, 'CONFIRMED');
INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES ('tx_d3_03', '90', 200, 'CONFIRMED');
