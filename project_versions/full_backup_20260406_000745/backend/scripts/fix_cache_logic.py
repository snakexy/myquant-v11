#!/usr/bin/env python3
"""修复缓存逻辑"""

with open('e:/MyQuant_v11/backend/src/myquant/core/market/services/seamless_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换盘后单层缓存逻辑
old_code1 = '''                        if cached_hash == current_hash:
                                logger.info(f"[Hash验证] {symbol} {period}: 缓存有效 (hash={cached_hash[:8]}...)，直接返回")
                                return self._ensure_naive_datetime(cached_data.copy())'''

new_code1 = '''                        if cached_hash == current_hash:
                                # [关键修复] Hash匹配后检查数据新鲜度
                                if self._is_cache_fresh(cached_data, period):
                                    logger.info(f"[Hash验证] {symbol} {period}: 缓存有效且数据新鲜 (hash={cached_hash[:8]}...)，直接返回")
                                    return self._ensure_naive_datetime(cached_data.copy())
                                else:
                                    logger.info(f"[Hash验证] {symbol} {period}: Hash有效但数据过期，触发增量获取")'''

if old_code1 in content:
    content = content.replace(old_code1, new_code1, 1)  # 只替换第一个（盘后）
    print('[OK] 盘后缓存逻辑修复完成')
else:
    print('[X] 未找到盘后缓存逻辑')

# 替换盘中双层缓存逻辑（类似的模式）
old_code2 = '''                            if cached_hash == current_hash:
                                    logger.info(f"[Hash验证] {symbol} {period}: 盘中缓存有效 (hash={cached_hash[:8]}...)，直接返回")
                                    return self._ensure_naive_datetime(cached_data.copy())'''

new_code2 = '''                            if cached_hash == current_hash:
                                    # [关键修复] Hash匹配后检查数据新鲜度
                                    if self._is_cache_fresh(cached_data, period):
                                        logger.info(f"[Hash验证] {symbol} {period}: 盘中缓存有效且新鲜 (hash={cached_hash[:8]}...)，直接返回")
                                        return self._ensure_naive_datetime(cached_data.copy())
                                    else:
                                        logger.info(f"[Hash验证] {symbol} {period}: 盘中Hash有效但数据过期，触发增量获取")'''

if old_code2 in content:
    content = content.replace(old_code2, new_code2, 1)
    print('[OK] 盘中缓存逻辑修复完成')
else:
    print('[X] 未找到盘中缓存逻辑')

# 保存
with open('e:/MyQuant_v11/backend/src/myquant/core/market/services/seamless_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('\n修复完成，重启后端服务生效')
