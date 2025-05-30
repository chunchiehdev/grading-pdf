#!/bin/bash

echo "Celery monitor_queue"
echo "================================"

while true; do
    clear
    echo "📊 Celery $(date)"
    echo "================================"
    
    QUEUE_LEN=$(docker exec grading-pdf-redis-1 redis-cli llen celery 2>/dev/null || echo "N/A")
    echo "📋 佇列中任務數量: $QUEUE_LEN"
    
    ACTIVE_COUNT=$(docker exec grading-pdf-worker-1 celery -A app.worker.celery_app inspect active 2>/dev/null | grep -c "parse_pdf_task" || echo "0")
    echo "🏃 正在處理任務: $ACTIVE_COUNT"
    
    echo ""
    echo "👷 Worker 狀態:"
    docker exec grading-pdf-worker-1 celery -A app.worker.celery_app inspect stats 2>/dev/null | grep -E "(pool|rusage-utime|rusage-stime)" | head -6
    
    REDIS_CLIENTS=$(docker exec grading-pdf-redis-1 redis-cli info clients 2>/dev/null | grep connected_clients | cut -d: -f2 | tr -d '\r')
    echo ""
    echo "🔌 Redis 連接數: $REDIS_CLIENTS"
    
    echo ""
    echo "⏰ 下次更新: 3秒後..."
    sleep 3
done 