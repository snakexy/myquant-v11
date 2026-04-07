import sys
with open('frontend/src/composables/useKlineData.ts', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''        // 增量模式：合并现有数据和新数据
        const isIncremental = enableIncremental && 'incremental' in res && res.incremental
        if (isIncremental && bars.value.length > 0) {
          // 合并数据（按时间戳去重）
          const existingMap = new Map(bars.value.map(b => [b.time, b]))
          for (const newBar of deduped) {
            existingMap.set(newBar.time, newBar)
          }
          const merged = Array.from(existingMap.values()).sort((a, b) => a.time - b.time)
          bars.value = merged
          rawBars.value = merged
          console.log(`[useKlineData] 增量合并: 新增 ${deduped.length} 条, 总计 ${merged.length} 条`)
        } else {
          // 全量模式：替换所有数据
          rawBars.value = deduped
          bars.value = deduped
        }'''

new = '''        // 增量模式：合并现有数据和新数据
        const isIncremental = enableIncremental && 'incremental' in res && res.incremental
        // 智能判断：如果返回数据量接近请求量(>=80%)，认为是全量而非增量
        const isActuallyIncremental = isIncremental && deduped.length < count * 0.8
        if (isActuallyIncremental && bars.value.length > 0) {
          // 合并数据（按时间戳去重）
          const existingMap = new Map(bars.value.map(b => [b.time, b]))
          for (const newBar of deduped) {
            existingMap.set(newBar.time, newBar)
          }
          const merged = Array.from(existingMap.values()).sort((a, b) => a.time - b.time)
          bars.value = merged
          rawBars.value = merged
          console.log(`[useKlineData] 增量合并: 新增 ${deduped.length} 条, 总计 ${merged.length} 条`)
        } else {
          // 全量模式：替换所有数据
          rawBars.value = deduped
          bars.value = deduped
          if (isIncremental) {
            console.log(`[useKlineData] 全量替换: ${deduped.length} 条 (返回数据>=80%请求量)`)
          }
        }'''

if old in content:
    content = content.replace(old, new)
    with open('frontend/src/composables/useKlineData.ts', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed!')
else:
    print('Pattern not found')
