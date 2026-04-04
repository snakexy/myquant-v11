#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    自动检查架构违规和代码规范
.DESCRIPTION
    在文件修改后自动运行，检查：
    1. Service层是否直接import Adapter
    2. 文件修改数量是否超过3个
    3. 是否有未完成的TODO
.EXAMPLE
    .\check-architecture.ps1
#>

# 颜色输出函数
function Write-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Error { Write-Host "❌ $args" -ForegroundColor Red }
function Write-Warning { Write-Host "⚠️  $args" -ForegroundColor Yellow }

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🔍 架构与规范自动检查" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$hasViolation = $false

# 1. 检查 Service 层是否直接 import Adapter
Write-Host "1️⃣ 检查架构约束（Service层不能直接import Adapter）..." -ForegroundColor White

$serviceDir = "backend/src/myquant/core/market/services"
if (Test-Path $serviceDir) {
    $violations = @()

    Get-ChildItem -Path $serviceDir -Filter "*.py" -Recurse | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -match "from\s+myquant\.core\.market\.adapters\.\w+\s+import") {
            $violations += $_.Name
        }
    }

    if ($violations.Count -gt 0) {
        Write-Error "Service层违规直接import Adapter:"
        $violations | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
        $hasViolation = $true
    } else {
        Write-Success "架构约束检查通过"
    }
}

Write-Host ""

# 2. 检查文件修改数量
Write-Host "2️⃣ 检查文件修改范围..." -ForegroundColor White

$gitStatus = git status --short 2>$null
$modifiedFiles = $gitStatus | Where-Object { $_ -match "^\s*M|^\s*A" }
$fileCount = ($modifiedFiles | Measure-Object).Count

if ($fileCount -gt 3) {
    Write-Error "修改文件数 ($fileCount) 超过3个，可能违反'单次只改1个功能'原则"
    Write-Host ""
    Write-Host "修改的文件:" -ForegroundColor Yellow
    $modifiedFiles | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    $hasViolation = $true
} else {
    Write-Success "修改范围检查通过 ($fileCount 个文件)"
}

Write-Host ""

# 3. 检查未完成的 TODO
Write-Host "3️⃣ 检查未完成的TODO..." -ForegroundColor White

$todos = git diff --cached -U0 | Select-String "TODO"
if ($todos) {
    Write-Warning "发现新增的TODO:"
    $todos | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
} else {
    Write-Success "无新增TODO"
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

if ($hasViolation) {
    Write-Host ""
    Write-Error "检查失败！请修复上述违规后再提交" -ForegroundColor Red
    Write-Host "   回滚命令: git reset --hard HEAD" -ForegroundColor Yellow
    Write-Host ""
    exit 1
} else {
    Write-Success "所有检查通过" -ForegroundColor Green
    Write-Host ""
    exit 0
}
