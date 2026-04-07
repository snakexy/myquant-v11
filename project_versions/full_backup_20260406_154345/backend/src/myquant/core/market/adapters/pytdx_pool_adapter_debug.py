    def _to_category(self, period: str) -> int:
        """转换周期"""
        category = self.PERIOD_CATEGORY.get(period, 9)
        logger.info(f"[周期映射] period={period} -> category={category}")
        return category
