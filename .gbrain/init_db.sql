-- lifedatabase SQLite FTS5 全文搜索数据库
-- 使用方式: sqlite3 .gbrain/gbrain.db < .gbrain/init_db.sql

-- 启用 WAL 模式
PRAGMA journal_mode=WAL;

-- 知识库索引表
CREATE TABLE IF NOT EXISTS kb_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    title TEXT,
    content TEXT,
    type TEXT,           -- concept, person, project, decision, insight, account
    tags TEXT,           -- JSON array
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- FTS5 全文搜索虚拟表
CREATE VIRTUAL TABLE IF NOT EXISTS kb_search USING fts5(
    path,
    title,
    content,
    tags,
    content='kb_index',
    content_rowid='id'
);

-- 关联表：概念关系
CREATE TABLE IF NOT EXISTS concept_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    target_id INTEGER,
    relation_type TEXT,  -- related, part_of, depends_on
    FOREIGN KEY (source_id) REFERENCES kb_index(id),
    FOREIGN KEY (target_id) REFERENCES kb_index(id)
);

-- 账号数据表
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    username TEXT,
    followers INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    posts INTEGER DEFAULT 0,
    state TEXT,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 采集历史表
CREATE TABLE IF NOT EXISTS collection_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    content_type TEXT,
    content_id TEXT,
    collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'success'
);

-- 触发器：更新 kb_search
CREATE TRIGGER IF NOT EXISTS kb_index_ai AFTER INSERT ON kb_index BEGIN
    INSERT INTO kb_search(rowid, path, title, content, tags) 
    VALUES (new.id, new.path, new.title, new.content, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS kb_index_ad AFTER DELETE ON kb_index BEGIN
    INSERT INTO kb_search(kb_search, rowid, path, title, content, tags) 
    VALUES ('delete', old.id, old.path, old.title, old.content, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS kb_index_au AFTER UPDATE ON kb_index BEGIN
    INSERT INTO kb_search(kb_search, rowid, path, title, content, tags) 
    VALUES ('delete', old.id, old.path, old.title, old.content, old.tags);
    INSERT INTO kb_search(rowid, path, title, content, tags) 
    VALUES (new.id, new.path, new.title, new.content, new.tags);
END;

-- 索引
CREATE INDEX IF NOT EXISTS idx_kb_type ON kb_index(type);
CREATE INDEX IF NOT EXISTS idx_kb_updated ON kb_index(updated_at);
CREATE INDEX IF NOT EXISTS idx_accounts_platform ON accounts(platform);
CREATE INDEX IF NOT EXISTS idx_collection_platform ON collection_history(platform);
