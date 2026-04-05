#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    检查是否存在计划文件，强制改前先计划
.DESCRIPTION
    在 Claude 修改代码文件前自动运行，确保已制定计划并经用户确认
.PARAMETER File
    被修改的文件路径
.PARAMETER Tool
    工具名称（Edit/Write）
.EXAMPLE
    .\plan-check.ps1 -File "backend/src/xxx.py" -Tool "Edit"
#>

param(
    [string]$File = "",
    [string]$Tool = ""
)

# 只检查代码文件（配置文件、文档不需要计划）
$codeExtensions = @(".py", ".ts", ".tsx", ".vue", ".js", ".jsx", ".java", ".go", ".rs")
$isCodeFile = $codeExtensions | Where-Object { $File.EndsWith($_) }

if (-not $isCodeFile) {
    # 非代码文件，允许通过
    exit 0
}

# 检查计划文件是否存在
$planFile = ".claude/plans/current-plan.md"

if (-not (Test-Path $planFile)) {
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
    Write-Host "❌ 错误：未找到计划文件" -ForegroundColor Red
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
    Write-Host ""
    Write-Host "必须先制定计划：" -ForegroundColor Yellow
    Write-Host "  1. 使用 EnterPlanMode 进入计划模式" -ForegroundColor Cyan
    Write-Host "  2. 制定计划并保存到 .claude/plans/current-plan.md" -ForegroundColor Cyan
    Write-Host "  3. 等待用户确认" -ForegroundColor Cyan
    Write-Host "  4. 然后才能修改代码" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
    Write-Host ""

    # 阻止操作
    exit 1
}

# 计划文件存在，读取并显示
$planContent = Get-Content $planFile -Raw -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "✅ 已找到计划文件" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""

# 显示计划摘要（前10行）
$planLines = $planContent -split "`n" | Select-Object -First 10
$planLines | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

Write-Host ""
Write-Host "如果计划已执行完毕，请删除计划文件：" -ForegroundColor Yellow
Write-Host "  rm .claude/plans/current-plan.md" -ForegroundColor Gray
Write-Host ""

# 允许操作
exit 0
