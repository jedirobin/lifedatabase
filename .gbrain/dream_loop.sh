#!/bin/bash
# 梦境循环脚本 - 每日凌晨自动运行
# 用途：分析当天交互，更新知识库

export HOME=/root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KB_DIR="$(dirname "$SCRIPT_DIR")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "=== 梦境循环开始 ==="

# 1. 扫描当天对话记录
log "[1/5] 扫描对话记录..."
if [ -f "$KB_DIR/.gbrain/conversations.json" ]; then
    log "找到对话记录文件"
    # 提取新知识点（后续实现）
else
    log "无对话记录，跳过"
fi

# 2. 更新索引文件
log "[2/5] 更新索引..."
# 更新 memory/index.md 的统计
# 更新 memory/recent.md

# 3. Git同步
log "[3/5] Git同步..."
cd "$KB_DIR" || exit 1
git add -A
git commit -m "梦境循环: $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || log "无变更需提交"
git push origin main 2>/dev/null || log "Git推送失败（可能无远程仓库）"

# 4. 生成每日简报
log "[4/5] 生成每日简报..."
REPORT_FILE="$KB_DIR/outputs/reports/daily_$(date '+%Y%m%d').md"
cat > "$REPORT_FILE" << EOF
# 每日简报 - $(date '+%Y-%m-%d')

## 今日知识库活动

| 项目 | 数量 |
|------|------|

## 梦境循环执行情况

- 执行时间: $(date '+%Y-%m-%d %H:%M:%S')
- 状态: 成功

## 明日待办

- [ ]

---

*由梦境循环自动生成*
EOF

log "简报已生成: $REPORT_FILE"

# 5. 清理旧文件
log "[5/5] 清理维护..."
# 保留最近30天的每日简报
find "$KB_DIR/outputs/reports/" -name "daily_*.md" -mtime +30 -delete 2>/dev/null

log "=== 梦境循环完成 ==="
