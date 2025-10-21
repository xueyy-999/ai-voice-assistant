"""
SQLite数据库管理
"""
import aiosqlite
from typing import Optional
from app.config import settings
from app.utils.logger import logger


class Database:
    """数据库管理类"""
    
    def __init__(self):
        self.db_path = settings.DATABASE_PATH
        self.conn: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        """建立数据库连接"""
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row
        return self.conn
    
    async def close(self):
        """关闭数据库连接"""
        if self.conn:
            await self.conn.close()
    
    async def execute(self, sql: str, params: tuple = ()):
        """执行SQL"""
        if not self.conn:
            await self.connect()
        async with self.conn.execute(sql, params) as cursor:
            await self.conn.commit()
            return cursor
    
    async def fetchone(self, sql: str, params: tuple = ()):
        """查询单条记录"""
        if not self.conn:
            await self.connect()
        async with self.conn.execute(sql, params) as cursor:
            return await cursor.fetchone()
    
    async def fetchall(self, sql: str, params: tuple = ()):
        """查询多条记录"""
        if not self.conn:
            await self.connect()
        async with self.conn.execute(sql, params) as cursor:
            return await cursor.fetchall()


# 全局数据库实例
db = Database()


async def init_database():
    """初始化数据库表结构"""
    await db.connect()
    
    # 创建会话表
    await db.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            context TEXT
        )
    """)
    
    # 创建消息表
    await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            type TEXT DEFAULT 'text',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    
    # 创建任务表
    await db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            intent TEXT,
            status TEXT DEFAULT 'pending',
            plan TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            result TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    
    # 创建任务步骤表
    await db.execute("""
        CREATE TABLE IF NOT EXISTS task_steps (
            id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            sequence INTEGER NOT NULL,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            params TEXT,
            result TEXT,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    """)
    
    # 创建工具调用表
    await db.execute("""
        CREATE TABLE IF NOT EXISTS tool_calls (
            id TEXT PRIMARY KEY,
            step_id TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            input TEXT,
            output TEXT,
            success BOOLEAN DEFAULT 0,
            error TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (step_id) REFERENCES task_steps(id)
        )
    """)
    
    logger.info("✅ Database tables created successfully")


__all__ = ["db", "init_database", "Database"]

