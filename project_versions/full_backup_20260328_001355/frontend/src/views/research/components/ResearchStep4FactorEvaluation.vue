<template>
  <div class="step-factor-evaluation-panel">
    <!-- 功能选项卡 -->
    <el-tabs v-model="activeTab" class="feature-tabs">
      <!-- 一键智能评估 -->
      <el-tab-pane :label="isZh ? '⚡ 一键智能评估' : '⚡ Smart Evaluation'" name="smart">
        <div class="tab-content">
          <div class="config-section">
            <h3 class="section-title">
              {{ isZh ? '已检测因子' : 'Detected Factors' }}
              <el-tag v-if="displayFactors.length > 0" type="info" size="small" style="margin-left: 10px;">
                {{ displayFactors.length }} {{ isZh ? '个' : 'factors' }}
              </el-tag>
            </h3>
            <div v-if="displayFactors.length > 0" class="factors-chips">
              <FactorTag
                v-for="factor in displayFactors"
                :key="factor.factor_name"
                :factor-name="factor.factor_name"
                :ic="factor.ic"
                :selected="smartSelectedFactors.includes(factor.factor_name)"
                clickable
                @click="toggleSmartFactor(factor.factor_name)"
                style="margin: 4px;"
              />
            </div>
            <el-alert v-else type="warning" :closable="false" show-icon style="margin-top: 12px;">
              {{ isZh ? '请先完成因子分析步骤' : 'Please complete factor analysis first' }}
            </el-alert>
          </div>

          <!-- 阈值配置 -->
          <div class="config-section">
            <h3 class="section-title">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>
              </svg>
              {{ isZh ? '评估阈值' : 'Evaluation Thresholds' }}
            </h3>
            <div class="threshold-config">
              <div class="threshold-item">
                <label>IC均值 ≥</label>
                <el-input-number v-model="evalConfig.icThreshold" :min="0" :max="0.2" :step="0.005" :precision="3" size="small" />
              </div>
              <div class="threshold-item">
                <label>IR ≥</label>
                <el-input-number v-model="evalConfig.irThreshold" :min="0" :max="3" :step="0.1" :precision="2" size="small" />
              </div>
              <div class="threshold-item">
                <label>{{ isZh ? 'IC正数占比' : 'IC Positive Ratio' }} ≥</label>
                <el-input-number v-model="evalConfig.icPositiveThreshold" :min="0" :max="1" :step="0.05" :precision="2" size="small" />
              </div>
            </div>
          </div>

          <div class="action-buttons" style="margin-top: 16px;">
            <ActionButton
              type="primary"
              :label="isSmartEvaluating ? (isZh ? '评估中...' : 'Evaluating...') : (isZh ? '一键智能评估' : 'Smart Evaluate')"
              :loading="isSmartEvaluating"
              :disabled="smartSelectedFactors.length === 0 || isSmartEvaluating"
              @click="runSmartEvaluation"
            />
          </div>

          <!-- 评估结果展示 -->
          <div v-if="evaluationResult.completed" class="result-section">
            <h3 class="section-title">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              {{ isZh ? '评估结果' : 'Evaluation Results' }}
            </h3>
            <div class="metrics-cards">
              <div class="metric-card">
                <div class="metric-label">{{ isZh ? '平均IC' : 'Avg IC' }}</div>
                <div class="metric-value" :class="{ pass: evaluationResult.icMean >= evalConfig.icThreshold }">
                  {{ evaluationResult.icMean?.toFixed(4) || '-' }}
                </div>
              </div>
              <div class="metric-card">
                <div class="metric-label">IR</div>
                <div class="metric-value" :class="{ pass: evaluationResult.ir >= evalConfig.irThreshold }">
                  {{ evaluationResult.ir?.toFixed(4) || '-' }}
                </div>
              </div>
              <div class="metric-card">
                <div class="metric-label">{{ isZh ? 'IC胜率' : 'IC Win Rate' }}</div>
                <div class="metric-value" :class="{ pass: evaluationResult.icPositiveRatio >= evalConfig.icPositiveThreshold }">
                  {{ evaluationResult.icPositiveRatio ? `${(evaluationResult.icPositiveRatio * 100).toFixed(1)}%` : '-' }}
                </div>
              </div>
              <div class="metric-card highlight">
                <div class="metric-label">{{ isZh ? '综合评分' : 'Overall Score' }}</div>
                <div class="metric-value">{{ overallScore.toFixed(2) }}</div>
              </div>
            </div>

            <!-- 指标详情表格 -->
            <div class="details-table-section">
              <el-table :data="metricsDetails" stripe border>
                <el-table-column :label="isZh ? '指标' : 'Metric'" prop="name" width="150" />
                <el-table-column :label="isZh ? '数值' : 'Value'" prop="value" width="120">
                  <template #default="{ row }">
                    {{ typeof row.value === 'number' ? row.value.toFixed(4) : row.value }}
                  </template>
                </el-table-column>
                <el-table-column :label="isZh ? '阈值' : 'Threshold'" prop="threshold" width="100">
                  <template #default="{ row }">
                    {{ row.threshold.toFixed(3) }}
                  </template>
                </el-table-column>
                <el-table-column :label="isZh ? '状态' : 'Status'" prop="passed" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.passed ? 'success' : 'danger'" size="small">
                      {{ row.passed ? (isZh ? '通过' : 'Pass') : (isZh ? '未通过' : 'Fail') }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column :label="isZh ? '评分' : 'Score'" prop="score">
                  <template #default="{ row }">
                    <el-progress
                      :percentage="Math.round(row.score * 100)"
                      :show-text="true"
                      :color="getScoreColor(row.score)"
                      :stroke-width="8"
                    />
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- 评分雷达图 - 因子库整体质量 -->
            <FactorQualityRadar
              :title="isZh ? '因子库整体质量' : 'Factor Library Quality'"
              :indicator="scoreIndicator"
              :indicator-values="scoreIndicatorValues"
              :data="scoreRadarData"
            />

            <!-- 建议 -->
            <div v-if="evaluationResult.recommendation" class="recommendation-box">
              <div class="rec-label">{{ isZh ? '建议' : 'Recommendation' }}:</div>
              <div class="rec-content">{{ evaluationResult.recommendation }}</div>
            </div>

            <!-- QLib标准指标 - 显著性检验 -->
            <div v-if="evaluationResult.completed" class="qlib-metrics-section">
              <h3 class="section-title">
                <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.35 3.35 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
                </svg>
                {{ isZh ? 'QLib标准 - 显著性检验' : 'QLib Standard - Significance Test' }}
              </h3>
              <div class="qlib-metrics-grid">
                <div class="qlib-metric-item">
                  <span class="qlib-metric-label">{{ isZh ? 't统计量' : 't-Statistic' }}</span>
                  <span class="qlib-metric-value" :class="{ pass: evaluationResult.tStat > 2 }">
                    {{ evaluationResult.tStat?.toFixed(4) || '-' }}
                  </span>
                  <span class="qlib-metric-desc">{{ isZh ? '>2 表示显著' : '>2 means significant' }}</span>
                </div>
                <div class="qlib-metric-item">
                  <span class="qlib-metric-label">{{ isZh ? 'p值' : 'p-Value' }}</span>
                  <span class="qlib-metric-value" :class="{ pass: evaluationResult.pValue < 0.05 }">
                    {{ evaluationResult.pValue < 0.0001 ? evaluationResult.pValue?.toExponential(2) : evaluationResult.pValue?.toFixed(4) || '-' }}
                  </span>
                  <span class="qlib-metric-desc">{{ isZh ? '<0.05 表示显著' : '<0.05 means significant' }}</span>
                </div>
                <div class="qlib-metric-item">
                  <span class="qlib-metric-label">{{ isZh ? 'IC标准差' : 'IC Std' }}</span>
                  <span class="qlib-metric-value">
                    {{ evaluationResult.icStd?.toFixed(4) || '-' }}
                  </span>
                  <span class="qlib-metric-desc">{{ isZh ? '越小越稳定' : 'Smaller is more stable' }}</span>
                </div>
                <div class="qlib-metric-item">
                  <span class="qlib-metric-label">{{ isZh ? 'Rank IC' : 'Rank IC' }}</span>
                  <span class="qlib-metric-value">
                    {{ evaluationResult.rankICMean?.toFixed(4) || '-' }}
                  </span>
                  <span class="qlib-metric-desc">{{ isZh ? '评估非线性关系' : 'Evaluate non-linear' }}</span>
                </div>
              </div>
            </div>

            <!-- IC时间序列 - 稳定性和衰减分析 -->
            <div v-if="evaluationResult.completed && evaluationResult.icSeries?.length > 0" class="ic-analysis-section">
              <h3 class="section-title">
                <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
                {{ isZh ? 'IC稳定性与衰减分析' : 'IC Stability & Decay Analysis' }}
              </h3>
              <div class="ic-stats-row">
                <div class="ic-stat-item">
                  <span class="ic-stat-label">{{ isZh ? 'IC序列长度' : 'IC Series Length' }}</span>
                  <span class="ic-stat-value">{{ evaluationResult.icSeries?.length || 0 }}</span>
                </div>
                <div class="ic-stat-item">
                  <span class="ic-stat-label">{{ isZh ? 'IC均值' : 'IC Mean' }}</span>
                  <span class="ic-stat-value">{{ computeICMean() }}</span>
                </div>
                <div class="ic-stat-item">
                  <span class="ic-stat-label">{{ isZh ? 'IC标准差' : 'IC Std' }}</span>
                  <span class="ic-stat-value">{{ evaluationResult.icStd?.toFixed(4) }}</span>
                </div>
                <div class="ic-stat-item">
                  <span class="ic-stat-label">{{ isZh ? '正IC天数' : 'Positive IC Days' }}</span>
                  <span class="ic-stat-value">{{ countPositiveIC() }}</span>
                </div>
              </div>
              <!-- IC序列可视化 -->
              <div class="ic-sequence-viz">
                <div class="ic-sequence-label">{{ isZh ? 'IC序列分布' : 'IC Sequence Distribution' }}</div>
                <div class="ic-bars-container">
                  <div
                    v-for="(ic, idx) in evaluationResult.icSeries?.slice(0, 50)"
                    :key="idx"
                    class="ic-bar"
                    :class="{ positive: ic > 0, negative: ic < 0 }"
                    :style="{ height: Math.min(Math.abs(ic) * 200, 20) + 'px' }"
                    :title="`Day ${idx + 1}: ${ic.toFixed(4)}`"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 因子评估 -->
      <el-tab-pane :label="isZh ? '因子评估' : 'Factor Evaluation'" name="evaluation">
        <div class="tab-content">
          <!-- 评估指标卡片 -->
          <div class="metrics-cards">
            <div class="metric-card">
              <div class="metric-label">{{ isZh ? '平均IC' : 'Avg IC' }}</div>
              <div class="metric-value">{{ evaluationResult.icMean?.toFixed(4) || '-' }}</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">IR</div>
              <div class="metric-value">{{ evaluationResult.ir?.toFixed(4) || '-' }}</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">{{ isZh ? 'IC胜率' : 'IC Win Rate' }}</div>
              <div class="metric-value">{{ evaluationResult.icPositiveRatio ? `${(evaluationResult.icPositiveRatio * 100).toFixed(1)}%` : '-' }}</div>
            </div>
            <div class="metric-card highlight">
              <div class="metric-label">{{ isZh ? '综合评分' : 'Overall Score' }}</div>
              <div class="metric-value">{{ overallScore.toFixed(2) }}</div>
            </div>
          </div>

          <!-- 评估配置 -->
          <div class="config-section">
            <h3>{{ isZh ? '评估配置' : 'Evaluation Config' }}</h3>
            <div class="config-form">
              <div class="form-group">
                <label>{{ isZh ? '评估方法' : 'Method' }}</label>
                <el-select v-model="evaluationConfig.method" style="width: 100%;">
                  <el-option :label="isZh ? 'IC/IR分析' : 'IC/IR Analysis'" value="icir"></el-option>
                  <el-option :label="isZh ? '因子组合' : 'Factor Combination'" value="combined"></el-option>
                </el-select>
              </div>
              <div class="form-group">
                <label>{{ isZh ? '评估周期' : 'Period' }}</label>
                <el-select v-model="evaluationConfig.period" style="width: 100%;">
                  <el-option :label="'20 ' + (isZh ? '天' : 'Days')" value="20d"></el-option>
                  <el-option :label="'60 ' + (isZh ? '天' : 'Days')" value="60d"></el-option>
                </el-select>
              </div>
            </div>
          </div>

          <!-- 因子选择（组合评估时显示） -->
          <div v-if="evaluationConfig.method === 'combined'" class="config-section">
            <h3>{{ isZh ? '因子选择' : 'Factor Selection' }}</h3>
            <el-select
              v-model="evaluationConfig.selectedFactors"
              multiple
              filterable
              :placeholder="isZh ? '选择因子（至少2个）' : 'Select factors (min 2)'"
              style="width: 100%;"
            >
              <el-option
                v-for="factor in displayFactors"
                :key="factor.factor_name"
                :label="factor.factor_name"
                :value="factor.factor_name"
              />
            </el-select>

            <!-- 组合方法 -->
            <div class="form-group" style="margin-top: 16px;">
              <label>{{ isZh ? '组合方法' : 'Combination Method' }}</label>
              <el-radio-group v-model="evaluationConfig.combinationMethod">
                <el-radio-button label="equal_weight">{{ isZh ? '等权重' : 'Equal Weight' }}</el-radio-button>
                <el-radio-button label="ic_weight">{{ isZh ? 'IC加权' : 'IC Weight' }}</el-radio-button>
              </el-radio-group>
            </div>
          </div>

          <!-- Tab2评估结果 -->
          <div v-if="evaluationResult.completed" class="result-section">
            <h3 class="section-title">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              {{ isZh ? '评估结果' : 'Evaluation Results' }}
            </h3>

            <!-- 指标详情表格 -->
            <div class="details-table-section">
              <el-table :data="metricsDetails" stripe border>
                <el-table-column :label="isZh ? '指标' : 'Metric'" prop="name" width="150" />
                <el-table-column :label="isZh ? '数值' : 'Value'" prop="value" width="120">
                  <template #default="{ row }">
                    {{ typeof row.value === 'number' ? row.value.toFixed(4) : row.value }}
                  </template>
                </el-table-column>
                <el-table-column :label="isZh ? '阈值' : 'Threshold'" prop="threshold" width="100">
                  <template #default="{ row }">
                    {{ row.threshold.toFixed(3) }}
                  </template>
                </el-table-column>
                <el-table-column :label="isZh ? '状态' : 'Status'" prop="passed" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.passed ? 'success' : 'danger'" size="small">
                      {{ row.passed ? (isZh ? '通过' : 'Pass') : (isZh ? '未通过' : 'Fail') }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column :label="isZh ? '评分' : 'Score'" prop="score">
                  <template #default="{ row }">
                    <el-progress
                      :percentage="Math.round(row.score * 100)"
                      :show-text="true"
                      :color="getScoreColor(row.score)"
                      :stroke-width="8"
                    />
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- 评分雷达图 - 因子库整体质量 -->
            <FactorQualityRadar
              :title="isZh ? '因子库整体质量' : 'Factor Library Quality'"
              :indicator="scoreIndicator"
              :indicator-values="scoreIndicatorValues"
              :data="scoreRadarData"
            />

            <!-- 建议 -->
            <div v-if="evaluationResult.recommendation" class="recommendation-box">
              <div class="rec-label">{{ isZh ? '建议' : 'Recommendation' }}:</div>
              <div class="rec-content">{{ evaluationResult.recommendation }}</div>
            </div>

            <!-- QLib标准指标 - 显著性检验 -->
            <div v-if="evaluationResult.completed" class="qlib-metrics-section">
              <h3 class="section-title">
                <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.35 3.35 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
                </svg>
                {{ isZh ? 'QLib标准 - 显著性检验' : 'QLib Standard - Significance Test' }}
              </h3>
              <div class="qlib-metrics-grid">
                <div class="qlib-metric-item">
                  <span class="qlib-metric-label">{{ isZh ? 't统计量' : 't-Statistic' }}</span>
                  <span class="qlib-metric-value" :class="{ pass: evaluationResult.tStat > 2 }">
                    {{ evaluationResult.tStat?.toFixed(4) || '-' }}
                  </span>
                  <span class="qlib-metric-desc">{{ isZh ? '>2 表示显著' : '>2 means significant' }}</span>
                </div>
                <div class="qlib-metric-item">
                  <span class="qlib-metric-label">{{ isZh ? 'p值' : 'p-Value' }}</span>
                  <span class="qlib-metric-value" :class="{ pass: evaluationResult.pValue < 0.05 }">
                    {{ evaluationResult.pValue < 0.0001 ? evaluationResult.pValue?.toExponential(2) : evaluationResult.pValue?.toFixed(4) || '-' }}
                  </span>
                  <span class="qlib-metric-desc">{{ isZh ? '<0.05 表示显著' : '<0.05 means significant' }}</span>
                </div>
                <div class="qlib-metric-item">
                  <span class="qlib-metric-label">{{ isZh ? 'IC标准差' : 'IC Std' }}</span>
                  <span class="qlib-metric-value">
                    {{ evaluationResult.icStd?.toFixed(4) || '-' }}
                  </span>
                  <span class="qlib-metric-desc">{{ isZh ? '越小越稳定' : 'Smaller is more stable' }}</span>
                </div>
                <div class="qlib-metric-item">
                  <span class="qlib-metric-label">{{ isZh ? 'Rank IC' : 'Rank IC' }}</span>
                  <span class="qlib-metric-value">
                    {{ evaluationResult.rankICMean?.toFixed(4) || '-' }}
                  </span>
                  <span class="qlib-metric-desc">{{ isZh ? '评估非线性关系' : 'Evaluate non-linear' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <ActionButton
        type="primary"
        :label="isEvaluating ? (isZh ? '评估中...' : 'Evaluating...') : (isZh ? '开始评估' : 'Start Evaluation')"
        :loading="isEvaluating"
        :disabled="isEvaluating"
        @click="runEvaluation"
      />
      <ActionButton
        type="success"
        :label="isZh ? '完成当前步骤' : 'Complete Step'"
        @click="completeStep"
      />
      <ActionButton
        type="default"
        :label="isZh ? '导出报告' : 'Export Report'"
        @click="exportReport"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import ActionButton from '@/components/ui/ActionButton.vue'
import FactorTag from '@/components/ui/FactorTag.vue'
import FactorQualityRadar from '@/components/ui/FactorQualityRadar.vue'
import { ElMessage } from 'element-plus'
import { factorEvaluationAPI as evalAPI } from '@/api/factorEvaluation'

interface Props {
  taskId?: string
  isZh?: boolean
  analyzedFactors?: any[]
}

interface FactorInfo {
  factor_name: string
  ic?: number
  ir?: number
  t_stat?: number
  p_value?: number
  status?: string
  category?: string  // 因子类型：动量、波动率、技术、成交量等
}

// 根据因子名称推断类型
const getFactorCategory = (factorName: string): string => {
  const name = factorName.toUpperCase()
  if (name.includes('MA') || name.includes('EMA') || name.includes('SMA') || name.includes('CROSS')) return 'momentum'
  if (name.includes('VOL') || name.includes('VOLUME')) return 'volume'
  if (name.includes('STD') || name.includes('VAR') || name.includes('STD_DEV')) return 'volatility'
  if (name.includes('RSI') || name.includes('MACD') || name.includes('KDJ') || name.includes('CCI')) return 'technical'
  if (name.includes('BETA') || name.includes('ALPHA')) return 'factor'
  if (name.includes('ROC') || name.includes('RETURN')) return 'momentum'
  return 'other'
}

// 获取因子类型对应的颜色
const getFactorCategoryColor = (category: string): string => {
  const colors: Record<string, string> = {
    momentum: '#26a69a',    // 绿色 - 动量
    volatility: '#ff9800',   // 橙色 - 波动率
    volume: '#2962ff',      // 蓝色 - 成交量
    technical: '#9c27b0',   // 紫色 - 技术
    factor: '#ef5350',      // 红色 - 因子
    other: '#787b86'        // 灰色 - 其他
  }
  return colors[category] || colors.other
}

const props = withDefaults(defineProps<Props>(), {
  taskId: '',
  isZh: true,
  analyzedFactors: () => []
})

const emit = defineEmits<{
  'dataUpdate': [data: any]
  'stepComplete': [data: { step: number; stats: any }]
}>()

// 完成当前步骤
const completeStep = () => {
  emit('stepComplete', { step: 4, stats: evaluationResult })
}

// 可用因子列表 - 从props获取
const displayFactors = computed<FactorInfo[]>(() => {
  if (props.analyzedFactors && props.analyzedFactors.length > 0) {
    return props.analyzedFactors
  }
  // 如果没有传入因子，返回空数组
  return []
})

// Tab状态
const activeTab = ref('smart')

// 智能评估选中的因子
const smartSelectedFactors = ref<string[]>([])

// 评估配置
const evaluationConfig = reactive({
  method: 'icir',
  period: '20d',
  selectedFactors: [] as string[],
  combinationMethod: 'equal_weight'
})

// 评估阈值配置
const evalConfig = reactive({
  icThreshold: 0.03,
  irThreshold: 0.5,
  icPositiveThreshold: 0.55
})

// 评估结果
const evaluationResult = reactive({
  icMean: 0,
  ir: 0,
  icPositiveRatio: 0,
  rankICMean: 0,
  // QLib标准指标
  icStd: 0,        // IC标准差 - 稳定性
  tStat: 0,        // t统计量 - 显著性
  pValue: 1,       // p值 - 显著性
  // IC时间序列 - 稳定性和衰减分析
  icSeries: [] as number[],
  completed: false,
  recommendation: '',
  isValid: false
})

const isEvaluating = ref(false)
const isSmartEvaluating = ref(false)

// 监听props变化，更新选中因子
watch(() => props.analyzedFactors, (newFactors) => {
  if (newFactors && newFactors.length > 0) {
    // 默认选中所有通过的因子
    smartSelectedFactors.value = newFactors
      .filter(f => f.status === 'pass' || (f.ic && f.ic > evalConfig.icThreshold))
      .map(f => f.factor_name)
  }
}, { immediate: true })

// 综合评分
const overallScore = computed(() => {
  if (!evaluationResult.completed) return 0
  // 使用绝对值处理负IC/IR
  const icScore = Math.max(0, Math.min((Math.abs(evaluationResult.icMean) / evalConfig.icThreshold) * 0.4, 1) * 40)
  const irScore = Math.max(0, Math.min((Math.abs(evaluationResult.ir) / evalConfig.irThreshold) * 0.3, 1) * 30)
  const winRateScore = evaluationResult.icPositiveRatio * 30
  return icScore + irScore + winRateScore
})

// 指标详情
const metricsDetails = computed(() => {
  if (!evaluationResult.completed) return []

  return [
    {
      name: props.isZh ? 'IC均值' : 'IC Mean',
      value: evaluationResult.icMean || 0,
      threshold: evalConfig.icThreshold,
      passed: (evaluationResult.icMean || 0) >= evalConfig.icThreshold,
      score: Math.max(0, Math.min(Math.abs(evaluationResult.icMean || 0) / evalConfig.icThreshold, 1))
    },
    {
      name: 'IR',
      value: evaluationResult.ir || 0,
      threshold: evalConfig.irThreshold,
      passed: (evaluationResult.ir || 0) >= evalConfig.irThreshold,
      score: Math.max(0, Math.min(Math.abs(evaluationResult.ir || 0) / evalConfig.irThreshold, 1))
    },
    {
      name: props.isZh ? 'IC胜率' : 'IC Win Rate',
      value: evaluationResult.icPositiveRatio || 0,
      threshold: evalConfig.icPositiveThreshold,
      passed: (evaluationResult.icPositiveRatio || 0) >= evalConfig.icPositiveThreshold,
      score: Math.min((evaluationResult.icPositiveRatio || 0) / evalConfig.icPositiveThreshold, 1)
    }
  ]
})

// 获取评分颜色
const getScoreColor = (score: number) => {
  if (score >= 0.8) return '#67c23a'
  if (score >= 0.6) return '#e6a23c'
  if (score >= 0.4) return '#f56c6c'
  return '#909399'
}

// 计算IC均值
const computeICMean = () => {
  const series = evaluationResult.icSeries
  if (!series || series.length === 0) return '-'
  const sum = series.reduce((a, b) => a + b, 0)
  return (sum / series.length).toFixed(4)
}

// 统计正IC天数
const countPositiveIC = () => {
  const series = evaluationResult.icSeries
  if (!series || series.length === 0) return 0
  return series.filter(ic => ic > 0).length
}

// 评分雷达图数据 - 供 RadarCard 使用（因子库整体质量布局）
const scoreIndicator = computed(() => [
  { name: props.isZh ? '平均IC' : 'Avg IC', max: 100 },
  { name: props.isZh ? 'IR比率' : 'IR Ratio', max: 100 },
  { name: props.isZh ? '通过率' : 'Pass Rate', max: 100 },
  { name: props.isZh ? '因子数量' : 'Factor Count', max: 100 }
])

// 行业基准值（评分标准化后）
const scoreBenchmark = computed(() => {
  // 行业标准：IC 3%, IR 0.4, 通过率 55%
  const icBenchmark = Math.min((0.03 / evalConfig.icThreshold) * 80, 100)
  const irBenchmark = Math.min((0.4 / evalConfig.irThreshold) * 80, 100)
  const winRateBenchmark = Math.min((0.55 / evalConfig.icPositiveThreshold) * 80, 100)
  const countBenchmark = 60 // 行业基准因子数量
  return [icBenchmark, irBenchmark, winRateBenchmark, countBenchmark].map(v => Math.round(v * 100) / 100)
})

// 真实数值（显示在指标列表中）
const scoreIndicatorValues = computed(() => {
  if (!evaluationResult.completed) return [0, 0, 0, 0]
  // 真实数值：IC均值、IR、通过率（百分比）、因子数量
  const icValue = evaluationResult.icMean || 0
  const irValue = evaluationResult.ir || 0
  const winRateValue = (evaluationResult.icPositiveRatio || 0) * 100 // 转为百分比
  const countValue = displayFactors.value.length
  return [icValue, irValue, winRateValue, countValue]
})

// 雷达图分数（转换后用于显示）
const scoreRadarValues = computed(() => {
  if (!evaluationResult.completed) return [0, 0, 0, 0]
  // 使用因子分析的转换公式：|IC|/0.05*80, |IR|/0.8*80
  // 使用绝对值处理负IC/IR，同时确保最小值为0
  const icScore = Math.max(0, Math.min((Math.abs(evaluationResult.icMean) / 0.05) * 80, 100))
  const irScore = Math.max(0, Math.min((Math.abs(evaluationResult.ir) / 0.8) * 80, 100))
  const passScore = Math.min((evaluationResult.icPositiveRatio / 0.55) * 80, 100)
  const countScore = Math.min((displayFactors.value.length / 200) * 80, 100)
  return [icScore, irScore, passScore, countScore].map(v => Math.round(v * 100) / 100)
})

const scoreRadarData = computed(() => {
  if (!evaluationResult.completed) return []
  const current = scoreRadarValues.value
  return [
    {
      name: props.isZh ? '当前因子库' : 'Current Library',
      value: current,
      color: '#409ee1',
      areaColor: 'rgba(64, 158, 225, 0.3)',
      lineType: 'solid' as const
    },
    {
      name: props.isZh ? '行业基准' : 'Benchmark',
      value: scoreBenchmark.value,
      color: '#ff9800',
      areaColor: 'rgba(255, 152, 0, 0.2)',
      lineType: 'dashed' as const
    }
  ]
})

// 切换因子选择
const toggleSmartFactor = (factorName: string) => {
  const index = smartSelectedFactors.value.indexOf(factorName)
  if (index > -1) {
    smartSelectedFactors.value.splice(index, 1)
  } else {
    smartSelectedFactors.value.push(factorName)
  }
}

// 运行智能评估
const runSmartEvaluation = async () => {
  if (smartSelectedFactors.value.length === 0) {
    ElMessage.warning(props.isZh ? '请选择至少一个因子' : 'Please select at least one factor')
    return
  }

  isSmartEvaluating.value = true
  try {
    if (smartSelectedFactors.value.length === 1) {
      // 单因子有效性验证
      const res = await evalAPI.evaluateValidity({
        factor_name: smartSelectedFactors.value[0],
        start_date: getDefaultStartDate(),
        end_date: getDefaultEndDate(),
        threshold: {
          ic_mean: evalConfig.icThreshold,
          ir: evalConfig.irThreshold,
          ic_positive_ratio: evalConfig.icPositiveThreshold
        }
      }) as any

      // 更新评估结果
      evaluationResult.icMean = res.metrics.ic_mean.value
      evaluationResult.ir = res.metrics.ir.value
      evaluationResult.icPositiveRatio = res.metrics.ic_positive_ratio.value
      // QLib标准指标
      evaluationResult.icStd = res.metrics.ic_std?.value || 0
      evaluationResult.tStat = res.metrics.t_stat?.value || 0
      evaluationResult.pValue = res.metrics.p_value?.value || 1
      evaluationResult.rankICMean = res.metrics.rank_ic_mean?.value || 0
      // IC时间序列
      evaluationResult.icSeries = res.ic_series || []
      evaluationResult.completed = true
      evaluationResult.isValid = res.is_valid
      evaluationResult.recommendation = res.recommendation
    } else {
      // 多因子组合评估
      const res = await evalAPI.evaluateCombination({
        factor_names: smartSelectedFactors.value,
        start_date: getDefaultStartDate(),
        end_date: getDefaultEndDate(),
        combination_method: evaluationConfig.combinationMethod as any
      }) as any

      evaluationResult.icMean = res.evaluation.ic_mean
      evaluationResult.ir = res.evaluation.ir
      evaluationResult.icPositiveRatio = res.evaluation.ic_positive_ratio
      evaluationResult.rankICMean = res.evaluation.rank_ic_mean
      evaluationResult.completed = true
      evaluationResult.isValid = true
      evaluationResult.recommendation = props.isZh
        ? `组合因子 ${res.combined_factor_name} 评估完成。IC: ${res.evaluation.ic_mean.toFixed(4)}, IR: ${res.evaluation.ir.toFixed(4)}`
        : `Combined factor ${res.combined_factor_name} evaluation completed. IC: ${res.evaluation.ic_mean.toFixed(4)}, IR: ${res.evaluation.ir.toFixed(4)}`
    }

    ElMessage.success(props.isZh ? '智能评估完成' : 'Smart evaluation completed')
    emit('dataUpdate', evaluationResult)
  } catch (error: any) {
    console.error('评估失败:', error)
    ElMessage.error(props.isZh ? '评估失败: ' + error.message : 'Evaluation failed: ' + error.message)

    // 降级到模拟数据
    evaluationResult.icMean = 0.045 + Math.random() * 0.02
    evaluationResult.ir = 0.6 + Math.random() * 0.3
    evaluationResult.icPositiveRatio = 0.5 + Math.random() * 0.15
    evaluationResult.completed = true
    evaluationResult.isValid = true
    evaluationResult.recommendation = props.isZh ? '（模拟数据）因子通过基本阈值' : '(Mock data) Factor passes basic threshold'
  } finally {
    isSmartEvaluating.value = false
  }
}

// 运行评估
const runEvaluation = async () => {
  isEvaluating.value = true
  try {
    if (evaluationConfig.method === 'icir') {
      // IC/IR分析评估 - 使用第一个因子
      const factors = displayFactors.value
      if (factors.length === 0) {
        ElMessage.warning(props.isZh ? '暂无因子可评估' : 'No factors to evaluate')
        return
      }

      const res1 = await evalAPI.evaluateValidity({
        factor_name: factors[0].factor_name,
        start_date: getDefaultStartDate(),
        end_date: getDefaultEndDate(),
        threshold: {
          ic_mean: evalConfig.icThreshold,
          ir: evalConfig.irThreshold,
          ic_positive_ratio: evalConfig.icPositiveThreshold
        }
      }) as any

      evaluationResult.icMean = res1.metrics.ic_mean.value
      evaluationResult.ir = res1.metrics.ir.value
      evaluationResult.icPositiveRatio = res1.metrics.ic_positive_ratio.value
      // QLib标准指标
      evaluationResult.icStd = res1.metrics.ic_std?.value || 0
      evaluationResult.tStat = res1.metrics.t_stat?.value || 0
      evaluationResult.pValue = res1.metrics.p_value?.value || 1
      evaluationResult.rankICMean = res1.metrics.rank_ic_mean?.value || 0
      // IC时间序列
      evaluationResult.icSeries = res1.ic_series || []
    } else if (evaluationConfig.method === 'combined') {
      // 组合评估
      if (evaluationConfig.selectedFactors.length < 2) {
        ElMessage.warning(props.isZh ? '请至少选择2个因子' : 'Please select at least 2 factors')
        return
      }

      const res2 = await evalAPI.evaluateCombination({
        factor_names: evaluationConfig.selectedFactors,
        start_date: getDefaultStartDate(),
        end_date: getDefaultEndDate(),
        combination_method: evaluationConfig.combinationMethod as any
      }) as any

      evaluationResult.icMean = res2.evaluation.ic_mean
      evaluationResult.ir = res2.evaluation.ir
      evaluationResult.icPositiveRatio = res2.evaluation.ic_positive_ratio
    }

    evaluationResult.completed = true
    ElMessage.success(props.isZh ? '评估完成' : 'Evaluation completed')
    emit('dataUpdate', evaluationResult)
  } catch (error: any) {
    console.error('评估失败:', error)
    // 降级到模拟数据
    evaluationResult.icMean = 0.045
    evaluationResult.ir = 0.78
    evaluationResult.icPositiveRatio = 0.55
    evaluationResult.completed = true
    ElMessage.warning(props.isZh ? '使用模拟数据' : 'Using mock data')
  } finally {
    isEvaluating.value = false
  }
}

// 导出报告
const exportReport = () => {
  ElMessage.info(props.isZh ? '导出功能开发中' : 'Export feature in development')
}

// 获取默认开始日期（1年前）
const getDefaultStartDate = () => {
  const date = new Date()
  date.setFullYear(date.getFullYear() - 1)
  return date.toISOString().split('T')[0]
}

// 获取默认结束日期（今天）
const getDefaultEndDate = () => {
  return new Date().toISOString().split('T')[0]
}
</script>

<style scoped lang="scss">
.step-factor-evaluation-panel {
  width: 100%;
}

.feature-tabs {
  margin-bottom: 20px;

  :deep(.el-tabs__header) {
    margin-bottom: 16px;
  }

  :deep(.el-tabs__item) {
    font-size: 14px;
    transition: none !important;
    &.is-active {
      color: var(--accent-blue) !important;
      &:hover {
        color: var(--accent-blue) !important;
      }
    }
    &:hover {
      color: var(--text-primary) !important;
    }
  }

  :deep(.el-tabs__active-bar) {
    background-color: var(--accent-blue);
  }

  :deep(.el-tabs__nav-wrap::after) {
    background-color: var(--border-color);
  }

  // 禁用tab的hover动画
  :deep(.el-tabs__item::after),
  :deep(.el-tabs__item::before) {
    transition: none !important;
  }
}

.tab-content {
  padding: 10px 0;
}

.config-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.icon-sm {
  width: 16px;
  height: 16px;
  color: var(--accent-blue);
}

.factors-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.factor-tag {
  // 左边彩色边框效果
  border-left: 3px solid #2962ff !important;
  border-radius: 0 4px 4px 0 !important;
  padding-left: 12px !important;

  &.is-warning {
    border-left-color: #2962ff !important;
  }

  &.is-info {
    border-left-color: #787b86 !important;
  }

  .factor-ic {
    font-size: 10px;
    opacity: 0.7;
    margin-left: 4px;
  }
}

.threshold-config {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 12px;
}

.threshold-item {
  display: flex;
  flex-direction: column;
  gap: 4px;

  label {
    font-size: 12px;
    color: var(--text-secondary);
  }
}

.result-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 16px;
  margin-top: 20px;
}

.metrics-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.metric-card {
  background: var(--bg-tertiary);
  border-radius: 6px;
  padding: 16px;
  text-align: center;
}

.metric-card.highlight {
  background: var(--accent-blue);
  color: white;

  .metric-label {
    color: rgba(255, 255, 255, 0.8);
  }
}

.metric-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--text-primary);

  &.pass {
    color: #67c23a;
  }
}

.metric-card.highlight .metric-value {
  color: white;
}

.config-form {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-group {
  margin-bottom: 12px;

  label {
    display: block;
    margin-bottom: 6px;
    font-size: 13px;
    color: var(--text-secondary);
  }
}

.details-table-section {
  margin-top: 16px;

  :deep(.el-table) {
    --el-table-bg-color: var(--bg-primary);
    --el-table-header-bg-color: var(--bg-tertiary);
    --el-table-text-color: var(--text-primary);
    --el-table-header-text-color: var(--text-primary);
    --el-table-border-color: var(--border-color);
    --el-table-row-hover-bg-color: var(--bg-tertiary);
  }
}

.recommendation-box {
  margin-top: 16px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 6px;
  border-left: 3px solid #67c23a;

  .rec-label {
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 4px;
  }

  .rec-content {
    font-size: 14px;
    color: var(--text-primary);
  }
}

.qlib-metrics-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 16px;
  margin-top: 16px;
}

.qlib-metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: 12px;
}

.qlib-metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 6px;
  text-align: center;
}

.qlib-metric-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.qlib-metric-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);

  &.pass {
    color: #67c23a;
  }
}

.qlib-metric-desc {
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.ic-analysis-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 16px;
  margin-top: 16px;
}

.ic-stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-top: 12px;
}

.ic-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  background: var(--bg-tertiary);
  border-radius: 6px;
}

.ic-stat-label {
  font-size: 11px;
  color: var(--text-secondary);
}

.ic-stat-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-top: 4px;
}

.ic-sequence-viz {
  margin-top: 16px;
}

.ic-sequence-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.ic-bars-container {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 40px;
  overflow-x: auto;
}

.ic-bar {
  width: 6px;
  min-height: 2px;
  border-radius: 1px;
  transition: height 0.2s;

  &.positive {
    background: #67c23a;
  }

  &.negative {
    background: #f56c6c;
  }
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2952cc;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-secondary);
}

.btn-success {
  background: var(--accent-green);
  color: white;
}

.btn-success:hover {
  background: #229a8f;
}
</style>
