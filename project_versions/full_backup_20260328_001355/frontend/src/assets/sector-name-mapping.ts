/**
 * 板块名称映射表
 * 将英文代码转换为中文显示名称
 */

export const SECTOR_NAME_MAPPING: Record<string, string> = {
  // 申万一级行业 (SW1)
  'sw1_agriculture': '农林牧渔',
  'sw1_automobile': '汽车',
  'sw1_banking': '银行',
  'sw1_building_materials': '建筑材料',
  'sw1_chemicals': '基础化工',
  'sw1_coal': '煤炭',
  'sw1_commerce': '商贸零售',
  'sw1_communication': '通信',
  'sw1_computer': '计算机',
  'sw1_conglomerates': '综合',
  'sw1_construction': '建筑装饰',
  'sw1_defense': '国防军工',
  'sw1_electronics': '电子',
  'sw1_environmental': '环保',
  'sw1_food_beverage': '食品饮料',
  'sw1_home_appliances': '家用电器',
  'sw1_light_manufacturing': '轻工制造',
  'sw1_machinery': '机械设备',
  'sw1_media': '传媒',
  'sw1_medicine_biology': '医药生物',
  'sw1_non_banking_finance': '非银金融',
  'sw1_non_ferrous_metals': '有色金属',
  'sw1_oil_petrochemicals': '石油石化',
  'sw1_power_equipment': '电力设备',
  'sw1_real_estate': '房地产',
  'sw1_social_services': '社会服务',
  'sw1_steel': '钢铁',
  'sw1_textile_apparel': '纺织服饰',
  'sw1_transportation': '交通运输',
  'sw1_utilities': '公用事业',
  'sw1_beauty_care': '美容护理',

  // 主要指数
  'hs300': '沪深300',
  'zz500': '中证500',
  'sz50': '上证50',
  'cyb': '创业板指',
  'kc50': '科创50',
  'zz1000': '中证1000',

  // 概念板块 (示例 - 需要根据实际数据补充)
  'concept_ai': '人工智能',
  'concept_new_energy': '新能源汽车',
  'concept_chip': '芯片半导体',
  'concept_5g': '5G通信',
  'concept_cloud_computing': '云计算',
  'concept_big_data': '大数据',
  'concept_blockchain': '区块链',
  'concept_quantum': '量子科技',
  'concept_biotech': '生物科技',
  'concept_medical': '医疗器械',
}

/**
 * 获取板块的中文显示名称
 * @param code 英文代码
 * @returns 中文名称，如果未找到则返回原代码
 */
export function getSectorDisplayName(code: string): string {
  return SECTOR_NAME_MAPPING[code] || code
}

/**
 * 批量转换板块名称
 * @param codes 英文代码数组
 * @returns 中文名称数组
 */
export function getSectorDisplayNames(codes: string[]): string[] {
  return codes.map(code => getSectorDisplayName(code))
}
