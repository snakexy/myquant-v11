#!/bin/bash
# -*- coding: utf-8 -*-
#
# 检查是否存在计划文件，强制改前先计划
# 在 Claude 修改代码文件前自动运行

FILE="$1"
TOOL="$2"

# 只检查代码文件
code_extensions="\.py$\.ts$\.tsx$\.vue$\.js$\.jsx$\.java$\.go$\.rs$"

is_code_file=0
for ext in py ts tsx vue js jsx java go rs; do
    if echo "$FILE" | grep -qE "\\.${ext}$"; then
        is_code_file=1
        break
    fi
done

if [ "$is_code_file" -eq 0 ]; then
    exit 0
fi

# 检查计划文件
PLAN_FILE=".claude/plans/current-plan.md"

if [ ! -f "$PLAN_FILE" ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ 错误：未找到计划文件"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "必须先制定计划："
    echo "  1. 使用 EnterPlanMode 进入计划模式"
    echo "  2. 制定计划并保存到 .claude/plans/current-plan.md"
    echo "  3. 等待用户确认"
    echo "  4. 然后才能修改代码"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    exit 1
fi

# 计划文件存在
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 已找到计划文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 显示计划摘要（前10行）
head -n 10 "$PLAN_FILE" | while read line; do
    echo "  $line"
done

echo ""
echo "如果计划已执行完毕，请删除计划文件："
echo "  rm .claude/plans/current-plan.md"
echo ""

exit 0
