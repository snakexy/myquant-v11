#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    检查文件修改范围是否符合预期
.DESCRIPTION
    在 Claude 修改文件后自动运行，显示本次改动的文件列表
    如果改动超过 3 个文件，输出警告
.PARAMETER File
    被修改的文件路径
.PARAMETER Task
    当前任务描述（可选）
.EXAMPLE
    .\check-file-scope.ps1 -File "backend/src/xxx.py" -Task "修复成交量单位"
#>

param(
    [string]$File = "",
    [string]$Task = ""
)

# 输出分隔线
function Print-Separator {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
}

# 获取当前 git 改动
$gitStatus = git status --short 2>$null
$modifiedFiles = $gitStatus | Where-Object { $_ -match "^\s*M|^\s*A|^\s*D" }

# 如果没有改动，退出
if (-not $modifiedFiles) {
    exit 0
}

# 统计改动文件数
$fileCount = ($modifiedFiles | Measure-Object).Count

Print-Separator
Write-Host "📊 本次改动统计" -ForegroundColor Cyan
Print-Separator

# 显示每个改动的文件
$modifiedFiles | ForEach-Object {
    $status = $_.Substring(0, 2).Trim()
    $file = $_.Substring(3)

    $color = switch ($status) {
        "M" { "Yellow" }
        "A" { "Green" }
        "D" { "Red" }
        default { "White" }
    }

    $symbol = switch ($status) {
        "M" { "📝" }
        "A" { "➕" }
        "D" { "🗑️" }
        default { "❓" }
    }

    Write-Host "  $symbol $file" -ForegroundColor $color
}

Print-Separator

# 如果超过 3 个文件，输出警告
if ($fileCount -gt 3) {
    Write-Host ""
    Write-Host "⚠️  警告：改动文件数 ($fileCount) 超过 3 个" -ForegroundColor Red
    Write-Host "    可能违反了'单次只改一个功能'的原则" -ForegroundColor Red
    Write-Host ""
    Write-Host "    如需回滚，执行：git reset --hard HEAD" -ForegroundColor Yellow
    Print-Separator
}

exit 0
