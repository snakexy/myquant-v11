# -*- coding: utf-8 -*-
"""
股票中文名称搜索工具
Stock Chinese Name Search Utility

职责：
- 中文转拼音
- 拼音首字母提取
- 模糊匹配
- 智能联想

版本: v1.0
创建日期: 2026-02-11
"""

import re
from typing import List, Dict, Tuple, Optional
from loguru import logger


class PinyinConverter:
    """
    拼音转换工具

    功能：
    - 中文转拼音
    - 提取首字母
    - 多音字处理
    """

    # 常用汉字拼音映射表（部分）
    # 实际使用时建议安装 pypinyin 库获得更完整的支持
    PINYIN_DICT = {
        # 阿拉伯数字
        '0': 'ling', '1': 'yi', '2': 'er', '3': 'san', '4': 'si',
        '5': 'wu', '6': 'liu', '7': 'qi', '8': 'ba', '9': 'jiu',

        # 常见姓氏
        '中': 'zhong', '国': 'guo', '平': 'ping', '安': 'an',
        '工': 'gong', '商': 'shang', '银': 'yin', '建': 'jian', '设': 'she',
        '农': 'nong', '业': 'ye', '中': 'zhong', '国': 'guo', '铁': 'tie', '建': 'jian',
        '交': 'jiao', '通': 'tong', '银': 'yin', '山': 'shan', '东': 'dong', '航': 'hang',
        '华': 'hua', '夏': 'xia', '银': 'yin', '河': 'he', '北': 'bei', '方': 'fang',
        '特': 'te', '锐': 'rui', '德': 'de', '邦': 'bang', '广': 'guang', '发': 'fa',
        '万': 'wan', '科': 'ke', '创': 'chuang', '达': 'da', '威': 'wei', '股': 'gu',
        '份': 'fen', '有': 'you', '限': 'xian', '公': 'gong', '司': 'si',

        # 行业常用字
        '银': 'yin', '行': 'hang', '证': 'zheng', '券': 'quan',
        '保': 'bao', '险': 'xian', '信': 'xin', '托': 'tuo',
        '房': 'fang', '地': 'di', '产': 'chan',

        # 地区常用字
        '上': 'shang', '海': 'hai', '深': 'shen', '圳': 'zhen',
        '北': 'bei', '京': 'jing', '广': 'guang', '州': 'zhou',
        '成': 'cheng', '都': 'du',

        # 股票常用字
        '集': 'ji', '团': 'tuan', '控': 'kong', '股': 'gu', '份': 'fen',
        '发': 'fa', '展': 'zhan', '科': 'ke', '技': 'ji', '有': 'you',
        '限': 'xian', '责': 'ze', '任': 'ren', '公': 'gong', '司': 'si',
        '实': 'shi', '业': 'ye', '集': 'ji', '团': 'tuan',
    }

    # 首字母映射（快速查找）
    FIRST_LETTER_MAP = {
        'zg': ['中国', '中钢', '中广'],
        'pa': ['平安'],
        'gf': ['发展', '光大'],
        'zt': ['中信', '中通'],
        'gs': ['工商', '国寿'],
        'js': ['建设', '金山', '江山'],
        'ny': ['农业', '南阳'],
        'yh': ['银行', '银河', '海运'],
        'zx': ['中信', '中心', '中医'],
        'jt': ['交通', '集团', '建投'],
        'hb': ['华宝', '华邦', '河北'],
        'hd': ['华夏', '恒大', '海德'],
        'gl': ['格力', '广电'],
        'mt': ['茅台', '民生', '美图'],
        'by': ['比亚迪', '白云'],
        'wk': ['万科', '五矿'],
        'sf': ['上证', '深发', '深纺'],
        'zj': ['基金', '中集', '中金'],
        'gf': ['国发', '广发'],
    }

    @classmethod
    def get_pinyin(cls, chinese_char: str) -> str:
        """
        获取汉字拼音

        Args:
            chinese_char: 单个汉字

        Returns:
            拼音字符串
        """
        if chinese_char in cls.PINYIN_DICT:
            return cls.PINYIN_DICT[chinese_char]

        # 尝试使用 pypinyin 库（如果安装）
        try:
            from pypinyin import lazy_pinyin
            result = lazy_pinyin(chinese_char)
            return result[0] if result else chinese_char
        except ImportError:
            logger.warning(f"pypinyin未安装，无法获取'{chinese_char}'的拼音")
            return chinese_char

    @classmethod
    def get_first_letters(cls, text: str) -> str:
        """
        获取文本的拼音首字母

        Args:
            text: 中文文本

        Returns:
            拼音首字母（小写）
        """
        if not text:
            return ''

        first_letters = []
        for char in text:
            if char in cls.PINYIN_DICT:
                pinyin = cls.PINYIN_DICT[char]
                first_letters.append(pinyin[0])
            elif char.isalpha():
                # 已经是字母
                first_letters.append(char.lower())
            # 忽略其他字符（数字、符号等）

        return ''.join(first_letters)

    @classmethod
    def get_full_pinyin(cls, text: str) -> str:
        """
        获取文本的完整拼音

        Args:
            text: 中文文本

        Returns:
            完整拼音（小写，用空格分隔）
        """
        if not text:
            return ''

        pinyin_list = []
        for char in text:
            if char in cls.PINYIN_DICT:
                pinyin_list.append(cls.PINYIN_DICT[char])
            elif char.isalpha():
                pinyin_list.append(char.lower())

        return ' '.join(pinyin_list)


class StockSearchEngine:
    """
    股票搜索引擎

    功能：
    - 中文名称精确匹配
    - 中文名称模糊匹配
    - 拼音首字母搜索
    - 拼音完整搜索
    - 智能联想
    - 索引缓存（Redis）
    """

    def __init__(self, enable_cache: bool = True):
        """
        初始化搜索引擎

        Args:
            enable_cache: 是否启用索引缓存
        """
        self.converter = PinyinConverter()
        self.stock_index = {}  # 股票索引 {symbol: stock_info}
        self.name_index = {}   # 名称索引 {name: [symbols]}
        self.pinyin_index = {} # 拼音索引 {pinyin: [symbols]}
        self.enable_cache = enable_cache
        self._cache_service = None
        self._index_loaded = False

    async def _get_cache_service(self):
        """获取缓存服务（延迟初始化）"""
        if self._cache_service is None and self.enable_cache:
            try:
                from .data_cache_service import get_data_cache_service
                self._cache_service = get_data_cache_service()
                await self._cache_service.initialize()
            except Exception as e:
                logger.warning(f"缓存服务初始化失败: {e}")
                self.enable_cache = False
        return self._cache_service

    async def load_index_from_cache(self) -> bool:
        """
        从缓存加载索引

        Returns:
            是否成功加载
        """
        if not self.enable_cache or self._index_loaded:
            return False

        try:
            cache_service = await self._get_cache_service()
            if not cache_service:
                return False

            from .data_cache_service import DataCacheKeyType

            # 加载股票索引
            stock_index_data = await cache_service.get(DataCacheKeyType.STOCK_SEARCH_INDEX, "stock")
            if stock_index_data:
                self.stock_index = stock_index_data
                logger.info(f"[缓存] 股票索引已加载: {len(self.stock_index)}条")

            # 加载名称索引
            name_index_data = await cache_service.get(DataCacheKeyType.STOCK_SEARCH_INDEX, "name")
            if name_index_data:
                self.name_index = name_index_data
                logger.info(f"[缓存] 名称索引已加载: {len(self.name_index)}条")

            # 加载拼音索引
            pinyin_index_data = await cache_service.get(DataCacheKeyType.STOCK_SEARCH_INDEX, "pinyin")
            if pinyin_index_data:
                self.pinyin_index = pinyin_index_data
                logger.info(f"[缓存] 拼音索引已加载: {len(self.pinyin_index)}条")

            self._index_loaded = bool(self.stock_index)
            return self._index_loaded

        except Exception as e:
            logger.warning(f"从缓存加载索引失败: {e}")
            return False

    async def save_index_to_cache(self) -> bool:
        """
        保存索引到缓存

        Returns:
            是否成功保存
        """
        if not self.enable_cache:
            return False

        try:
            cache_service = await self._get_cache_service()
            if not cache_service:
                return False

            from .data_cache_service import DataCacheKeyType

            # 保存股票索引
            await cache_service.set(DataCacheKeyType.STOCK_SEARCH_INDEX, self.stock_index, "stock")
            await cache_service.set(DataCacheKeyType.STOCK_SEARCH_INDEX, self.name_index, "name")
            await cache_service.set(DataCacheKeyType.STOCK_SEARCH_INDEX, self.pinyin_index, "pinyin")

            logger.info(f"[缓存] 索引已保存: stock={len(self.stock_index)}, name={len(self.name_index)}, pinyin={len(self.pinyin_index)}")
            return True

        except Exception as e:
            logger.warning(f"保存索引到缓存失败: {e}")
            return False

    async def ensure_index(self, stocks: List[Dict]) -> None:
        """
        确保索引已构建（优先从缓存加载）

        Args:
            stocks: 用于构建索引的股票列表（仅在缓存未命中时使用）
        """
        # 如果索引已存在，直接返回
        if self.stock_index:
            return

        # 尝试从缓存加载
        if await self.load_index_from_cache():
            return

        # 缓存未命中，构建新索引
        self.build_index(stocks)

        # 保存到缓存
        await self.save_index_to_cache()

    def build_index(self, stocks: List[Dict]) -> None:
        """
        构建搜索索引

        Args:
            stocks: 股票列表，格式：[{"symbol": "000001.SZ", "name": "平安银行", ...}]
        """
        logger.info(f"构建股票搜索索引，股票数: {len(stocks)}")

        for stock in stocks:
            symbol = stock.get('symbol', '')
            name = stock.get('name', '')

            if not symbol or not name:
                continue

            # 添加到股票索引
            self.stock_index[symbol] = stock

            # 添加到名称索引
            if name not in self.name_index:
                self.name_index[name] = []
            self.name_index[name].append(symbol)

            # 添加到拼音索引
            first_letters = self.converter.get_first_letters(name)
            full_pinyin = self.converter.get_full_pinyin(name)

            if first_letters:
                if first_letters not in self.pinyin_index:
                    self.pinyin_index[first_letters] = []
                self.pinyin_index[first_letters].append(symbol)

            if full_pinyin:
                if full_pinyin not in self.pinyin_index:
                    self.pinyin_index[full_pinyin] = []
                self.pinyin_index[full_pinyin].append(symbol)

        logger.info(f"索引构建完成: 名称索引={len(self.name_index)}, 拼音索引={len(self.pinyin_index)}")


    def search(
        self,
        query: str,
        limit: int = 20,
        search_type: str = "all"
    ) -> List[Dict]:
        """
        搜索股票

        Args:
            query: 搜索关键词（中文/拼音首字母/拼音完整）
            limit: 返回结果数量限制
            search_type: 搜索类型（exact/prefix/fuzzy/all）

        Returns:
            匹配的股票列表
        """
        if not query:
            return []

        query = query.strip().lower()
        results = []
        seen_symbols = set()

        # 1. 精确匹配（股票代码或名称）
        if search_type in ['exact', 'all']:
            # 匹配股票代码
            for symbol, info in self.stock_index.items():
                if query in symbol.lower():
                    if symbol not in seen_symbols:
                        results.append(info)
                        seen_symbols.add(symbol)
                        if len(results) >= limit:
                            return results[:limit]

            # 匹配名称
            for name, symbols in self.name_index.items():
                if query in name.lower():
                    for symbol in symbols:
                        if symbol not in seen_symbols:
                            results.append(self.stock_index.get(symbol))
                            seen_symbols.add(symbol)
                            if len(results) >= limit:
                                return results[:limit]

        # 2. 拼音首字母匹配
        if search_type in ['prefix', 'fuzzy', 'all'] and len(query) <= 5:
            # 匹配拼音首字母
            for pinyin, symbols in self.pinyin_index.items():
                if pinyin.startswith(query):
                    for symbol in symbols:
                        if symbol not in seen_symbols:
                            results.append(self.stock_index.get(symbol))
                            seen_symbols.add(symbol)
                            if len(results) >= limit:
                                return results[:limit]

        # 3. 模糊匹配（拼音或名称）
        if search_type in ['fuzzy', 'all']:
            for name, symbols in self.name_index.items():
                # 名称模糊匹配
                for char in query:
                    if char.isalpha() and char in name:
                        if all(symbols):
                            for symbol in symbols[:3]:  # 限制数量
                                if symbol not in seen_symbols:
                                    results.append(self.stock_index.get(symbol))
                                    seen_symbols.add(symbol)
                                    if len(results) >= limit:
                                        return results[:limit]

        return results[:limit]

    def suggest(self, query: str, limit: int = 10) -> List[Dict]:
        """
        智能联想（返回搜索建议）

        Args:
            query: 搜索关键词
            limit: 返回建议数量

        Returns:
            建议的股票列表
        """
        if not query or len(query) < 1:
            return []

        query = query.strip().lower()
        suggestions = []
        seen_symbols = set()

        # 优先返回精确匹配
        exact_matches = self.search(query, limit=5, search_type='exact')
        for stock in exact_matches:
            symbol = stock.get('symbol', '')
            if symbol not in seen_symbols:
                suggestions.append({
                    **stock,
                    'match_type': 'exact',
                    'match_score': 100
                })
                seen_symbols.add(symbol)

        # 返回拼音首字母匹配
        if len(query) >= 2:
            prefix_matches = self.search(query, limit=5, search_type='prefix')
            for stock in prefix_matches:
                symbol = stock.get('symbol', '')
                if symbol not in seen_symbols:
                    suggestions.append({
                        **stock,
                        'match_type': 'pinyin',
                        'match_score': 80
                    })
                    seen_symbols.add(symbol)

        return suggestions[:limit]


# ==================== 全局单例 ====================

_stock_search_engine: Optional[StockSearchEngine] = None


def get_stock_search_engine() -> StockSearchEngine:
    """
    获取股票搜索引擎单例

    Returns:
        StockSearchEngine实例
    """
    global _stock_search_engine

    if _stock_search_engine is None:
        _stock_search_engine = StockSearchEngine()
        logger.info("✅ 股票搜索引擎初始化完成")

    return _stock_search_engine


# ==================== 测试代码 ====================

if __name__ == "__main__":
    # 测试拼音转换
    print("=== 拼音转换测试 ===")

    # 测试首字母提取
    test_names = ["中国平安", "招商银行", "贵州茅台", "比亚迪"]
    for name in test_names:
        first_letters = PinyinConverter.get_first_letters(name)
        full_pinyin = PinyinConverter.get_full_pinyin(name)
        print(f"{name}: 首字母={first_letters}, 拼音={full_pinyin}")

    # 测试搜索引擎
    print("\n=== 搜索引擎测试 ===")

    # 模拟股票数据
    test_stocks = [
        {"symbol": "000001.SZ", "name": "平安银行", "market": "SZ"},
        {"symbol": "000002.SZ", "name": "万科A", "market": "SZ"},
        {"symbol": "600036.SH", "name": "招商银行", "market": "SH"},
        {"symbol": "600519.SH", "name": "贵州茅台", "market": "SH"},
        {"symbol": "002594.SZ", "name": "比亚迪", "market": "SZ"},
        {"symbol": "601318.SH", "name": "中国平安", "market": "SH"},
    ]

    # 构建索引
    engine = StockSearchEngine()
    engine.build_index(test_stocks)

    # 测试搜索
    test_queries = ["平安", "pa", "zg", "茅台", "byd"]
    for query in test_queries:
        results = engine.search(query, limit=5)
        print(f"\n搜索 '{query}':")
        for r in results:
            print(f"  - {r['symbol']} {r['name']}")
