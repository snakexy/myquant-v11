<template>
  <teleport to="body">
    <div v-if="visible" class="indicator-settings-overlay" @click="handleCancel"></div>
    <div
      v-if="visible"
      class="indicator-settings-panel"
      :style="panelStyle"
      @click.stop
    >
      <div class="settings-header">
        <span>{{ config?.name }} 参数设置</span>
        <button class="settings-close-btn" @click="handleCancel">×</button>
      </div>

      <div class="settings-content">
        <!-- MA特殊处理：均线线条设置（带可见性复选框） -->
        <div v-if="indicatorId === 'MA'" class="settings-section">
          <div class="section-title">均线设置</div>
          <div v-for="line in maLineOptions" :key="line.key" class="line-setting-row">
            <!-- 可见性复选框 -->
            <label class="ma-visibility-checkbox">
              <input
                type="checkbox"
                :checked="visibleMaLines.includes(line.key)"
                @change="toggleMaLine(line.key)"
              />
            </label>
            <!-- 线条名称 -->
            <span class="line-label" :style="{ color: getLineColor(line.key, line.color) }">
              {{ line.label }}
            </span>
            <!-- 线条控制（颜色、线型、线宽） -->
            <div class="line-controls">
              <input
                type="color"
                :value="getLineColor(line.key, line.color)"
                @input="setLineColor(line.key, ($event.target as HTMLInputElement).value)"
                class="color-input"
              />
              <select
                :value="getLineStyle(line.key)"
                @change="setLineStyle(line.key, ($event.target as HTMLSelectElement).value)"
                class="style-select"
              >
                <option value="0">━━━ 实线</option>
                <option value="1">--- 虚线</option>
                <option value="2">··· 点线</option>
                <option value="3">·-·- 点虚线</option>
              </select>
              <input
                type="number"
                :value="getLineWidth(line.key, line.lineWidth || 1)"
                @input="setLineWidth(line.key, ($event.target as HTMLInputElement).value)"
                min="1"
                max="5"
                class="width-input"
              />
            </div>
          </div>
        </div>

        <!-- BOLL线条设置 -->
        <div v-else-if="indicatorId === 'BOLL'" class="settings-section">
          <div class="section-title">线条设置</div>
          <div v-for="line in bollLineOptions" :key="line.key" class="line-setting-row">
            <!-- 可见性复选框 -->
            <label class="ma-visibility-checkbox">
              <input
                type="checkbox"
                :checked="visibleBollLines.includes(line.key)"
                @change="toggleBollLine(line.key)"
              />
            </label>
            <!-- 线条名称 -->
            <span class="line-label" :style="{ color: getLineColor(line.key, line.color) }">
              {{ line.label }}
            </span>
            <!-- 线条控制（颜色、线型、线宽） -->
            <div class="line-controls">
              <input
                type="color"
                :value="getLineColor(line.key, line.color)"
                @input="setLineColor(line.key, ($event.target as HTMLInputElement).value)"
                class="color-input"
              />
              <select
                :value="getLineStyle(line.key)"
                @change="setLineStyle(line.key, ($event.target as HTMLSelectElement).value)"
                class="style-select"
              >
                <option value="0">━━━ 实线</option>
                <option value="1">--- 虚线</option>
                <option value="2">··· 点线</option>
                <option value="3">·-·- 点虚线</option>
              </select>
              <input
                type="number"
                :value="getLineWidth(line.key, 1)"
                @input="setLineWidth(line.key, ($event.target as HTMLInputElement).value)"
                min="1"
                max="5"
                class="width-input"
              />
            </div>
          </div>
        </div>

        <!-- SKDJ/KDJ/RSI 区域设置 -->
        <div v-else-if="['SKDJ', 'KDJ', 'RSI'].includes(indicatorId)" class="settings-section">
          <div class="section-title">区域设置</div>

          <!-- 超买区域 -->
          <div class="area-setting-row">
            <span class="area-label">超买区域 (>{{ getAreaOverboughtThreshold() }})</span>
            <div class="area-controls">
              <input
                type="color"
                :value="getAreaColor('overbought', '#F44336')"
                @input="setAreaColor('overbought', ($event.target as HTMLInputElement).value)"
                class="color-input"
              />
              <input
                type="range"
                :value="getAreaOpacity('overbought', 50)"
                @input="setAreaOpacity('overbought', ($event.target as HTMLInputElement).value)"
                min="5"
                max="80"
                class="opacity-slider"
              />
              <span class="opacity-value">{{ getAreaOpacity('overbought', 50) }}%</span>
            </div>
          </div>

          <!-- 超卖区域 -->
          <div class="area-setting-row">
            <span class="area-label">超卖区域 (<{{ getAreaOversoldThreshold() }})</span>
            <div class="area-controls">
              <input
                type="color"
                :value="getAreaColor('oversold', '#4CAF50')"
                @input="setAreaColor('oversold', ($event.target as HTMLInputElement).value)"
                class="color-input"
              />
              <input
                type="range"
                :value="getAreaOpacity('oversold', 50)"
                @input="setAreaOpacity('oversold', ($event.target as HTMLInputElement).value)"
                min="5"
                max="80"
                class="opacity-slider"
              />
              <span class="opacity-value">{{ getAreaOpacity('oversold', 50) }}%</span>
            </div>
          </div>

          <!-- 显示警戒线复选框 -->
          <div class="alert-line-row">
            <label class="alert-line-checkbox">
              <input
                type="checkbox"
                :checked="getShowAlertLines()"
                @change="setShowAlertLines(($event.target as HTMLInputElement).checked)"
              />
              <span class="checkbox-label">显示警戒线</span>
            </label>
          </div>
        </div>

        <!-- SMC 指标设置 -->
        <div v-else-if="indicatorId === 'SMC'" class="settings-section">
          <div class="section-title">SMC 参数</div>

          <!-- 数值参数 -->
          <div class="param-row">
            <span class="param-label">摆动点周期</span>
            <input
              type="number"
              :value="getSmcParam('swing_length', 5)"
              @input="setSmcParam('swing_length', ($event.target as HTMLInputElement).value)"
              min="1"
              max="50"
              class="param-input"
            />
          </div>

          <!-- 参考线设置（最近N根K线最高/最低） -->
          <div class="smc-element-section">
            <div class="smc-element-header">
              <label class="smc-checkbox">
                <input
                  type="checkbox"
                  :checked="getSmcParam('show_reference', true)"
                  @change="setSmcParam('show_reference', ($event.target as HTMLInputElement).checked)"
                />
              </label>
              <span class="smc-label reference-label">参考线 (最高/最低)</span>
            </div>
            <div v-if="getSmcParam('show_reference', true)" class="smc-element-controls">
              <div class="control-row">
                <span class="control-label">参考周期</span>
                <input
                  type="number"
                  :value="getSmcParam('reference_period', 34)"
                  @input="setSmcParam('reference_period', ($event.target as HTMLInputElement).value)"
                  min="5"
                  max="200"
                  class="count-input"
                />
              </div>
              <div class="control-row">
                <span class="control-label">线条颜色</span>
                <input
                  type="color"
                  :value="getSmcColor('reference_color', '#FFD700')"
                  @input="setSmcColor('reference_color', ($event.target as HTMLInputElement).value)"
                  class="color-input small"
                />
              </div>
              <div class="control-row">
                <span class="control-label">线条样式</span>
                <select
                  :value="getSmcParam('reference_line_style', 2)"
                  @change="setSmcParam('reference_line_style', ($event.target as HTMLSelectElement).value)"
                  class="style-select small"
                >
                  <option value="0">━━━ 实线</option>
                  <option value="1">--- 虚线</option>
                  <option value="2">··· 点线</option>
                  <option value="3">·-·- 点虚线</option>
                </select>
              </div>
              <div class="control-row">
                <span class="control-label">线条宽度</span>
                <input
                  type="number"
                  :value="getSmcParam('reference_line_width', 1)"
                  @input="setSmcParam('reference_line_width', ($event.target as HTMLInputElement).value)"
                  min="0.5"
                  max="5"
                  step="0.5"
                  class="count-input"
                />
              </div>
              <div class="control-row">
                <span class="control-label">透明度</span>
                <input
                  type="range"
                  :value="getSmcParam('reference_opacity', 80)"
                  @input="setSmcParam('reference_opacity', ($event.target as HTMLInputElement).value)"
                  min="20"
                  max="100"
                  class="opacity-slider"
                />
                <span class="opacity-value">{{ getSmcParam('reference_opacity', 80) }}%</span>
              </div>
            </div>
          </div>

          <!-- FVG 设置 -->
          <div class="smc-element-section">
            <div class="smc-element-header">
              <label class="smc-checkbox">
                <input
                  type="checkbox"
                  :checked="getSmcParam('show_fvg', true)"
                  @change="setSmcParam('show_fvg', ($event.target as HTMLInputElement).checked)"
                />
              </label>
              <span class="smc-label fvg-label">FVG 公平价值缺口</span>
            </div>
            <div v-if="getSmcParam('show_fvg', true)" class="smc-element-controls">
              <div class="control-row">
                <span class="control-label">看涨颜色</span>
                <input
                  type="color"
                  :value="getSmcColor('fvg_bullish', '#4CAF50')"
                  @input="setSmcColor('fvg_bullish', ($event.target as HTMLInputElement).value)"
                  class="color-input small"
                />
              </div>
              <div class="control-row">
                <span class="control-label">看跌颜色</span>
                <input
                  type="color"
                  :value="getSmcColor('fvg_bearish', '#F44336')"
                  @input="setSmcColor('fvg_bearish', ($event.target as HTMLInputElement).value)"
                  class="color-input small"
                />
              </div>
              <div class="control-row">
                <span class="control-label">透明度</span>
                <input
                  type="range"
                  :value="getSmcParam('fvg_opacity', 12)"
                  @input="setSmcParam('fvg_opacity', ($event.target as HTMLInputElement).value)"
                  min="5"
                  max="80"
                  class="opacity-slider"
                />
                <span class="opacity-value">{{ getSmcParam('fvg_opacity', 12) }}%</span>
              </div>
              <div class="control-row">
                <span class="control-label">显示数量</span>
                <input
                  type="number"
                  :value="getSmcParam('fvg_count', 5)"
                  @input="setSmcParam('fvg_count', ($event.target as HTMLInputElement).value)"
                  min="1"
                  max="20"
                  class="count-input"
                />
              </div>
              <div class="control-row">
                <span class="control-label">边框样式</span>
                <select
                  :value="getSmcParam('fvg_line_style', 1)"
                  @change="setSmcParam('fvg_line_style', ($event.target as HTMLSelectElement).value)"
                  class="style-select small"
                >
                  <option value="0">━━━ 实线</option>
                  <option value="1">--- 虚线</option>
                  <option value="2">··· 点线</option>
                  <option value="3">·-·- 点虚线</option>
                </select>
              </div>
              <div class="control-row">
                <span class="control-label">边框宽度</span>
                <input
                  type="number"
                  :value="getSmcParam('fvg_line_width', 1)"
                  @input="setSmcParam('fvg_line_width', ($event.target as HTMLInputElement).value)"
                  min="0.5"
                  max="5"
                  step="0.5"
                  class="count-input"
                />
              </div>
              <div class="control-row">
                <span class="control-label">边框透明度</span>
                <input
                  type="range"
                  :value="getSmcParam('fvg_border_opacity', 100)"
                  @input="setSmcParam('fvg_border_opacity', ($event.target as HTMLInputElement).value)"
                  min="20"
                  max="100"
                  class="opacity-slider"
                />
                <span class="opacity-value">{{ getSmcParam('fvg_border_opacity', 100) }}%</span>
              </div>
            </div>
          </div>

          <!-- OB 设置 -->
          <div class="smc-element-section">
            <div class="smc-element-header">
              <label class="smc-checkbox">
                <input
                  type="checkbox"
                  :checked="getSmcParam('show_ob', true)"
                  @change="setSmcParam('show_ob', ($event.target as HTMLInputElement).checked)"
                />
              </label>
              <span class="smc-label ob-label">OB 订单块</span>
            </div>
            <div v-if="getSmcParam('show_ob', true)" class="smc-element-controls">
              <div class="control-row">
                <span class="control-label">看涨颜色</span>
                <input
                  type="color"
                  :value="getSmcColor('ob_bullish', '#00D9FF')"
                  @input="setSmcColor('ob_bullish', ($event.target as HTMLInputElement).value)"
                  class="color-input small"
                />
              </div>
              <div class="control-row">
                <span class="control-label">看跌颜色</span>
                <input
                  type="color"
                  :value="getSmcColor('ob_bearish', '#FF61D2')"
                  @input="setSmcColor('ob_bearish', ($event.target as HTMLInputElement).value)"
                  class="color-input small"
                />
              </div>
              <div class="control-row">
                <span class="control-label">透明度</span>
                <input
                  type="range"
                  :value="getSmcParam('ob_opacity', 15)"
                  @input="setSmcParam('ob_opacity', ($event.target as HTMLInputElement).value)"
                  min="5"
                  max="80"
                  class="opacity-slider"
                />
                <span class="opacity-value">{{ getSmcParam('ob_opacity', 15) }}%</span>
              </div>
              <div class="control-row">
                <span class="control-label">边框样式</span>
                <select
                  :value="getSmcParam('ob_line_style', 0)"
                  @change="setSmcParam('ob_line_style', ($event.target as HTMLSelectElement).value)"
                  class="style-select small"
                >
                  <option value="0">━━━ 实线</option>
                  <option value="1">--- 虚线</option>
                  <option value="2">··· 点线</option>
                  <option value="3">·-·- 点虚线</option>
                </select>
              </div>
              <div class="control-row">
                <span class="control-label">边框宽度</span>
                <input
                  type="number"
                  :value="getSmcParam('ob_border_width', 2)"
                  @input="setSmcParam('ob_border_width', ($event.target as HTMLInputElement).value)"
                  min="0.5"
                  max="5"
                  step="0.5"
                  class="count-input"
                />
              </div>
              <div class="control-row">
                <span class="control-label">边框透明度</span>
                <input
                  type="range"
                  :value="getSmcParam('ob_border_opacity', 100)"
                  @input="setSmcParam('ob_border_opacity', ($event.target as HTMLInputElement).value)"
                  min="20"
                  max="100"
                  class="opacity-slider"
                />
                <span class="opacity-value">{{ getSmcParam('ob_border_opacity', 100) }}%</span>
              </div>
              <div class="control-row">
                <span class="control-label">显示数量</span>
                <input
                  type="number"
                  :value="getSmcParam('ob_count', 5)"
                  @input="setSmcParam('ob_count', ($event.target as HTMLInputElement).value)"
                  min="1"
                  max="20"
                  class="count-input"
                />
              </div>
            </div>
          </div>

          <!-- 摆动点设置 -->
          <div class="smc-element-section">
            <div class="smc-element-header">
              <label class="smc-checkbox">
                <input
                  type="checkbox"
                  :checked="getSmcParam('show_swing_points', true)"
                  @change="setSmcParam('show_swing_points', ($event.target as HTMLInputElement).checked)"
                />
              </label>
              <span class="smc-label swing-label">摆动点 (HH/HL/LL/LH)</span>
            </div>
            <div v-if="getSmcParam('show_swing_points', true)" class="smc-element-controls">
              <div class="control-row">
                <span class="control-label">高点颜色</span>
                <input
                  type="color"
                  :value="getSmcColor('swing_high_color', '#00D9FF')"
                  @input="setSmcColor('swing_high_color', ($event.target as HTMLInputElement).value)"
                  class="color-input small"
                />
              </div>
              <div class="control-row">
                <span class="control-label">低点颜色</span>
                <input
                  type="color"
                  :value="getSmcColor('swing_low_color', '#FF61D2')"
                  @input="setSmcColor('swing_low_color', ($event.target as HTMLInputElement).value)"
                  class="color-input small"
                />
              </div>
              <div class="control-row">
                <span class="control-label">标签大小</span>
                <input
                  type="number"
                  :value="getSmcParam('swing_font_size', 10)"
                  @input="setSmcParam('swing_font_size', ($event.target as HTMLInputElement).value)"
                  min="8"
                  max="16"
                  class="count-input"
                />
              </div>
            </div>
          </div>

          <!-- BMS 设置 -->
          <div class="smc-element-section">
            <div class="smc-element-header">
              <label class="smc-checkbox">
                <input
                  type="checkbox"
                  :checked="getSmcParam('show_bms', true)"
                  @change="setSmcParam('show_bms', ($event.target as HTMLInputElement).checked)"
                />
              </label>
              <span class="smc-label bos-label">BMS 结构突破 <span class="label-hint" title="趋势延续信号">↡涨破前高 (上升趋势) 或 ↓跌破前低 (下降趋势)</span></span>
            </div>
            <div v-if="getSmcParam('show_bms', true)" class="smc-element-controls">
              <div class="control-row">
                <span class="control-label">颜色</span>
                <input
                  type="color"
                  :value="getSmcColor('bms_color', '#FFD700')"
                  @input="setSmcColor('bms_color', ($event.target as HTMLInputElement).value)"
                  class="color-input small"
                />
              </div>
              <div class="control-row">
                <span class="control-label">方块大小</span>
                <input
                  type="number"
                  :value="getSmcParam('bms_box_size', 8)"
                  @input="setSmcParam('bms_box_size', ($event.target as HTMLInputElement).value)"
                  min="3"
                  max="15"
                  class="count-input"
                />
              </div>
              <div class="control-row">
                <span class="control-label">线条样式</span>
                <select
                  :value="getSmcParam('bms_line_style', 1)"
                  @change="setSmcParam('bms_line_style', ($event.target as HTMLSelectElement).value)"
                  class="style-select small"
                >
                  <option value="0">━━━ 实线</option>
                  <option value="1">--- 虚线</option>
                  <option value="2">··· 点线</option>
                  <option value="3">·-·- 点虚线</option>
                </select>
              </div>
              <div class="control-row">
                <span class="control-label">线条宽度</span>
                <input
                  type="number"
                  :value="getSmcParam('bms_line_width', 1)"
                  @input="setSmcParam('bms_line_width', ($event.target as HTMLInputElement).value)"
                  min="0.5"
                  max="5"
                  step="0.5"
                  class="count-input"
                />
              </div>
              <div class="control-row">
                <span class="control-label">显示数量</span>
                <input
                  type="number"
                  :value="getSmcParam('bms_count', 5)"
                  @input="setSmcParam('bms_count', ($event.target as HTMLInputElement).value)"
                  min="1"
                  max="20"
                  class="count-input"
                />
              </div>
              <div class="control-row">
                <span class="control-label">线条透明度</span>
                <input
                  type="range"
                  :value="getSmcParam('bms_opacity', 100)"
                  @input="setSmcParam('bms_opacity', ($event.target as HTMLInputElement).value)"
                  min="20"
                  max="100"
                  class="opacity-slider"
                />
                <span class="opacity-value">{{ getSmcParam('bms_opacity', 100) }}%</span>
              </div>
            </div>
          </div>

          <!-- CHoCH 设置 -->
          <div class="smc-element-section">
            <div class="smc-element-header">
              <label class="smc-checkbox">
                <input
                  type="checkbox"
                  :checked="getSmcParam('show_choch', true)"
                  @change="setSmcParam('show_choch', ($event.target as HTMLInputElement).checked)"
                />
              </label>
              <span class="smc-label choch-label">CHoCH 市场结构转变 <span class="label-hint" title="趋势反转信号">↓涨破前高 (下降趋势) 或 ↓跌破前低 (上升趋势)</span></span>
            </div>
            <div v-if="getSmcParam('show_choch', true)" class="smc-element-controls">
              <div class="control-row">
                <span class="control-label">颜色</span>
                <input
                  type="color"
                  :value="getSmcColor('choch_color', '#9C27B0')"
                  @input="setSmcColor('choch_color', ($event.target as HTMLInputElement).value)"
                  class="color-input small"
                />
              </div>
              <div class="control-row">
                <span class="control-label">菱形大小</span>
                <input
                  type="number"
                  :value="getSmcParam('choch_diamond_size', 6)"
                  @input="setSmcParam('choch_diamond_size', ($event.target as HTMLInputElement).value)"
                  min="3"
                  max="12"
                  class="count-input"
                />
              </div>
              <div class="control-row">
                <span class="control-label">线条样式</span>
                <select
                  :value="getSmcParam('choch_line_style', 1)"
                  @change="setSmcParam('choch_line_style', ($event.target as HTMLSelectElement).value)"
                  class="style-select small"
                >
                  <option value="0">━━━ 实线</option>
                  <option value="1">--- 虚线</option>
                  <option value="2">··· 点线</option>
                  <option value="3">·-·- 点虚线</option>
                </select>
              </div>
              <div class="control-row">
                <span class="control-label">线条宽度</span>
                <input
                  type="number"
                  :value="getSmcParam('choch_line_width', 1)"
                  @input="setSmcParam('choch_line_width', ($event.target as HTMLInputElement).value)"
                  min="0.5"
                  max="5"
                  step="0.5"
                  class="count-input"
                />
              </div>
              <div class="control-row">
                <span class="control-label">显示数量</span>
                <input
                  type="number"
                  :value="getSmcParam('choch_count', 5)"
                  @input="setSmcParam('choch_count', ($event.target as HTMLInputElement).value)"
                  min="1"
                  max="20"
                  class="count-input"
                />
              </div>
              <div class="control-row">
                <span class="control-label">线条透明度</span>
                <input
                  type="range"
                  :value="getSmcParam('choch_opacity', 100)"
                  @input="setSmcParam('choch_opacity', ($event.target as HTMLInputElement).value)"
                  min="20"
                  max="100"
                  class="opacity-slider"
                />
                <span class="opacity-value">{{ getSmcParam('choch_opacity', 100) }}%</span>
              </div>
            </div>
          </div>

          <!-- SMC 说明 -->
          <div class="smc-description">
            <div class="desc-item"><strong>BMS 结构突破</strong> - 趋势延续信号</div>
            <div class="desc-item"><strong>CHoCH 市场结构转变</strong> - 趋势反转信号</div>
          </div>
        </div>

        <!-- 通用指标：MACD/KDJ/RSI等 -->
        <template v-else>
          <!-- 数值参数 -->
          <div v-if="Object.keys(numericParams).length > 0" class="settings-section">
            <div class="section-title">参数设置</div>
            <div v-for="(value, key) in numericParams" :key="key" class="param-row">
              <span class="param-label">{{ getParamLabel(key as string) }}</span>
              <input
                type="number"
                :value="getParamValue(key as string, value)"
                @input="setParamValue(key as string, ($event.target as HTMLInputElement).value)"
                min="1"
                max="200"
                class="param-input"
              />
            </div>
          </div>

          <!-- 线条设置 -->
          <div v-if="lineSettings.length > 0" class="settings-section">
            <div class="section-title">线条设置</div>
            <div v-for="line in lineSettings" :key="line.key" class="line-setting-row">
              <span class="line-label" :style="{ color: getLineColor(line.key, line.color) }">
                {{ line.label }}
              </span>
              <div class="line-controls">
                <input
                  type="color"
                  :value="getLineColor(line.key, line.color)"
                  @input="setLineColor(line.key, ($event.target as HTMLInputElement).value)"
                  class="color-input"
                />
                <select
                  :value="getLineStyle(line.key)"
                  @change="setLineStyle(line.key, ($event.target as HTMLSelectElement).value)"
                  class="style-select"
                >
                  <option value="0">━━━ 实线</option>
                  <option value="1">--- 虚线</option>
                  <option value="2">··· 点线</option>
                  <option value="3">·-·- 点虚线</option>
                </select>
                <input
                  type="number"
                  :value="getLineWidth(line.key, line.lineWidth || 2)"
                  @input="setLineWidth(line.key, ($event.target as HTMLInputElement).value)"
                  min="1"
                  max="5"
                  class="width-input"
                />
              </div>
            </div>
          </div>
        </template>
      </div>

      <div class="settings-footer">
        <button class="settings-btn reset" @click="handleReset">恢复默认</button>
        <button class="settings-btn cancel" @click="handleCancel">取消</button>
        <button class="settings-btn confirm" @click="handleConfirm">应用</button>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { getIndicatorConfig } from './indicator-registry'

interface Props {
  visible: boolean
  indicatorId: string
  currentParams: Record<string, any>
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
  confirm: [params: Record<string, any>]
  cancel: []
}>()

const formValue = ref<Record<string, any>>({})
const visibleMaLines = ref<string[]>(['ma5', 'ma10', 'ma20', 'ma30', 'ma60'])
const visibleBollLines = ref<string[]>(['upper', 'middle', 'lower'])

// 面板位置
const panelStyle = {
  position: 'fixed' as const,
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  zIndex: 1001
}

// 获取指标配置
const config = computed(() => getIndicatorConfig(props.indicatorId))

// MA线条选项
const maLineOptions = [
  { key: 'ma5', label: 'MA5', color: '#FFFFFF' },
  { key: 'ma10', label: 'MA10', color: '#FFFF00' },
  { key: 'ma20', label: 'MA20', color: '#FF00FF' },
  { key: 'ma30', label: 'MA30', color: '#00FFFF' },
  { key: 'ma60', label: 'MA60', color: '#00FF00' }
]

// BOLL线条选项
const bollLineOptions = [
  { key: 'upper', label: '上轨', color: '#FF6B6B' },
  { key: 'middle', label: '中轨', color: '#26A69A' },
  { key: 'lower', label: '下轨', color: '#FF6B6B' }
]

// 通用指标：数值参数
const numericParams = computed(() => {
  const result: Record<string, number> = {}
  const c = config.value
  if (!c?.defaultParams) return result

  Object.entries(c.defaultParams).forEach(([key, value]) => {
    if (typeof value === 'number' && !Array.isArray(value)) {
      result[key] = value
    }
  })
  return result
})

// 通用指标：线条设置
const lineSettings = computed(() => {
  return config.value?.series || []
})

// 参数标签映射
const paramLabels: Record<string, string> = {
  fast: '快线周期',
  slow: '慢线周期',
  signal: '信号周期',
  kPeriod: 'K周期',
  dPeriod: 'D周期',
  jPeriod: 'J周期',
  period: '周期',
  stdDev: '标准差'
}

function getParamLabel(key: string): string {
  return paramLabels[key] || key
}

function getParamValue(key: string, defaultValue: number): number {
  return formValue.value[key] ?? defaultValue
}

function setParamValue(key: string, value: string) {
  formValue.value[key] = parseInt(value) || 1
}

function getLineColor(key: string, defaultColor: string): string {
  return formValue.value[key]?.color || defaultColor
}

function setLineColor(key: string, color: string) {
  if (!formValue.value[key]) formValue.value[key] = {}
  formValue.value[key].color = color
}

function getLineStyle(key: string): number {
  return formValue.value[key]?.lineStyle ?? 0
}

function setLineStyle(key: string, style: string) {
  if (!formValue.value[key]) formValue.value[key] = {}
  formValue.value[key].lineStyle = parseInt(style)
}

function getLineWidth(key: string, defaultWidth: number): number {
  return formValue.value[key]?.lineWidth || defaultWidth
}

function setLineWidth(key: string, width: string) {
  if (!formValue.value[key]) formValue.value[key] = {}
  formValue.value[key].lineWidth = Math.max(1, Math.min(5, parseInt(width) || 1))
}

function toggleMaLine(key: string) {
  const index = visibleMaLines.value.indexOf(key)
  if (index > -1) {
    visibleMaLines.value.splice(index, 1)
  } else {
    visibleMaLines.value.push(key)
  }
}

function toggleBollLine(key: string) {
  const index = visibleBollLines.value.indexOf(key)
  if (index > -1) {
    visibleBollLines.value.splice(index, 1)
  } else {
    visibleBollLines.value.push(key)
  }
}

// SMC 参数获取
function getSmcParam(key: string, defaultValue: any): any {
  const val = formValue.value[key]
  // 如果值是 null、undefined 或空字符串，返回默认值
  if (val === null || val === undefined || val === '') {
    return defaultValue
  }
  return val
}

// SMC 参数设置
function setSmcParam(key: string, value: any) {
  if (typeof value === 'string') {
    // 数字类型转换
    if (['swing_length', 'fvg_opacity', 'fvg_count', 'fvg_line_style', 'fvg_line_width', 'fvg_border_opacity',
         'ob_opacity', 'ob_border_width', 'ob_border_opacity', 'ob_line_style', 'ob_count',
         'swing_font_size', 'bms_box_size', 'bms_line_style', 'bms_line_width', 'bms_count', 'bms_opacity',
         'choch_diamond_size', 'choch_line_style', 'choch_line_width', 'choch_line_length', 'choch_count', 'choch_opacity',
         'reference_period', 'reference_line_style', 'reference_line_width', 'reference_opacity'].includes(key)) {
      const parsed = parseInt(value)
    formValue.value[key] = isNaN(parsed) ? defaultValueFor(key) : parsed
    } else {
      formValue.value[key] = value === 'true'
    }
  } else {
    formValue.value[key] = value
  }
}

function defaultValueFor(key: string): number {
  const defaults: Record<string, number> = {
    swing_length: 5,
    fvg_opacity: 12,
    fvg_count: 5,
    fvg_line_style: 1,
    fvg_line_width: 1,
    fvg_border_opacity: 100,
    ob_opacity: 15,
    ob_border_width: 2,
    ob_border_opacity: 100,
    ob_line_style: 0,
    ob_count: 5,
    swing_font_size: 10,
    bms_box_size: 8,
    bms_line_style: 1,
    bms_line_width: 1,
    bms_count: 5,
    bms_opacity: 100,
    choch_diamond_size: 6,
    choch_line_style: 1,
    choch_line_width: 1,
    choch_count: 5,
    choch_opacity: 100,
    reference_period: 34,
    reference_line_style: 2,
    reference_line_width: 1,
    reference_opacity: 80
  }
  return defaults[key] || 1
}

// SMC 颜色获取
function getSmcColor(key: string, defaultColor: string): string {
  return formValue.value[key] || defaultColor
}

// SMC 颜色设置
function setSmcColor(key: string, color: string) {
  formValue.value[key] = color
}

// 区域设置：获取超买/超卖阈值
function getAreaOverboughtThreshold(): number {
  if (props.indicatorId === 'KDJ' || props.indicatorId === 'SKDJ') return 80
  if (props.indicatorId === 'RSI') return 70
  return 80
}

function getAreaOversoldThreshold(): number {
  if (props.indicatorId === 'KDJ' || props.indicatorId === 'SKDJ') return 20
  if (props.indicatorId === 'RSI') return 30
  return 20
}

// 区域颜色获取
function getAreaColor(type: 'overbought' | 'oversold', defaultColor: string): string {
  const key = `area_${type}_color`
  return formValue.value[key] || defaultColor
}

// 区域颜色设置
function setAreaColor(type: 'overbought' | 'oversold', color: string) {
  const key = `area_${type}_color`
  formValue.value[key] = color
}

// 区域透明度获取
function getAreaOpacity(type: 'overbought' | 'oversold', defaultOpacity: number): number {
  const key = `area_${type}_opacity`
  return formValue.value[key] || defaultOpacity
}

// 区域透明度设置
function setAreaOpacity(type: 'overbought' | 'oversold', opacity: string) {
  const key = `area_${type}_opacity`
  formValue.value[key] = parseInt(opacity) || 50
}

// 是否显示警戒线
function getShowAlertLines(): boolean {
  return formValue.value.show_alert_lines !== false  // 默认显示
}

function setShowAlertLines(show: boolean) {
  formValue.value.show_alert_lines = show
}

// 初始化表单
function initForm() {
  if (!config.value) return

  if (props.currentParams && Object.keys(props.currentParams).length > 0) {
    formValue.value = JSON.parse(JSON.stringify(props.currentParams))
  } else {
    formValue.value = {}
  }

  // 初始化MA可见性
  if (props.indicatorId === 'MA') {
    visibleMaLines.value = formValue.value.visibleLines || ['ma5', 'ma10', 'ma20', 'ma30', 'ma60']
  }

  // 初始化BOLL可见性
  if (props.indicatorId === 'BOLL') {
    visibleBollLines.value = formValue.value.visibleLines || ['upper', 'middle', 'lower']
  }

  // 初始化线条设置（使用默认值）
  config.value.series?.forEach(s => {
    if (!formValue.value[s.key]) {
      formValue.value[s.key] = {
        color: s.color,
        lineStyle: 0,
        lineWidth: s.lineWidth || 2
      }
    }
  })

  // 初始化 SMC 参数默认值（如果未设置）
  if (props.indicatorId === 'SMC') {
    const smcDefaults = {
      swing_length: 5,
      show_fvg: true,
      fvg_opacity: 12,
      fvg_count: 5,
      fvg_line_style: 1,
      fvg_line_width: 1,
      fvg_border_opacity: 100,
      fvg_bullish: '#4CAF50',
      fvg_bearish: '#F44336',
      show_ob: true,
      ob_opacity: 15,
      ob_border_width: 2,
      ob_border_opacity: 100,
      ob_count: 5,
      ob_line_style: 0,
      ob_line_width: 2,
      ob_bullish: '#00D9FF',
      ob_bearish: '#FF61D2',
      show_swing_points: true,
      swing_high_color: '#00D9FF',
      swing_low_color: '#FF61D2',
      show_bms: true,
      bms_color: '#FFD700',
      bms_box_size: 8,
      bms_line_style: 1,
      bms_line_width: 1,
      bms_count: 5,
      bms_opacity: 100,
      show_choch: true,
      choch_color: '#9C27B0',
      choch_diamond_size: 6,
      choch_line_style: 1,
      choch_line_width: 1,
      choch_line_length: 100,
      choch_count: 5,
      choch_opacity: 100,
      show_reference: true,
      reference_period: 34,
      reference_color: '#FFD700',
      reference_line_style: 2,
      reference_line_width: 1,
      reference_opacity: 80
    }

    Object.entries(smcDefaults).forEach(([key, value]) => {
      if (formValue.value[key] === undefined || formValue.value[key] === null || formValue.value[key] === '') {
        formValue.value[key] = value
      }
    })
  }

  // 初始化 SKDJ/KDJ/RSI 区域设置默认值
  if (['SKDJ', 'KDJ', 'RSI'].includes(props.indicatorId)) {
    const areaDefaults = {
      area_overbought_color: '#F44336',
      area_overbought_opacity: 50,
      area_oversold_color: '#4CAF50',
      area_oversold_opacity: 50,
      show_alert_lines: true
    }

    Object.entries(areaDefaults).forEach(([key, value]) => {
      if (formValue.value[key] === undefined || formValue.value[key] === null || formValue.value[key] === '') {
        formValue.value[key] = value
      }
    })
  }
}

// 监听打开时初始化
watch(() => props.visible, (newVal) => {
  if (newVal) initForm()
})

function handleCancel() {
  emit('cancel')
  emit('update:visible', false)
}

function handleReset() {
  formValue.value = {}
  visibleMaLines.value = ['ma5', 'ma10', 'ma20', 'ma30', 'ma60']
  visibleBollLines.value = ['upper', 'middle', 'lower']
  initForm()
}

function handleConfirm() {
  const result: Record<string, any> = { ...formValue.value }

  // MA：保存可见线条
  if (props.indicatorId === 'MA') {
    result.visibleLines = [...visibleMaLines.value]
  }

  // BOLL：保存可见线条
  if (props.indicatorId === 'BOLL') {
    result.visibleLines = [...visibleBollLines.value]
  }

  emit('confirm', result)
  emit('update:visible', false)
}
</script>

<style scoped>
.indicator-settings-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.indicator-settings-panel {
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
  min-width: 320px;
  max-width: 400px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.settings-header {
  padding: 12px 16px;
  border-bottom: 1px solid #2a2e39;
  font-size: 14px;
  font-weight: 600;
  color: #d1d4dc;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.settings-close-btn {
  background: none;
  border: none;
  color: #787b86;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.settings-close-btn:hover {
  color: #d1d4dc;
}

.settings-content {
  padding: 16px;
  overflow-y: auto;
  flex: 1;
}

.settings-section {
  margin-bottom: 16px;
}

.settings-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 12px;
  color: #787b86;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.ma-visibility-checkbox {
  display: flex;
  align-items: center;
  margin-right: 8px;
  min-width: 20px;
}

.ma-visibility-checkbox input[type="checkbox"] {
  width: 14px;
  height: 14px;
  cursor: pointer;
  margin: 0;
}

.line-setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #2a2e39;
}

.line-setting-row:last-child {
  border-bottom: none;
}

.line-label {
  font-size: 13px;
  min-width: 50px;
}

.line-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-input {
  width: 28px;
  height: 28px;
  border: 1px solid #2a2e39;
  border-radius: 4px;
  cursor: pointer;
  background: none;
  padding: 2px;
}

.color-input::-webkit-color-swatch-wrapper {
  padding: 0;
}

.color-input::-webkit-color-swatch {
  border: none;
  border-radius: 2px;
}

.style-select {
  background: #2a2e39;
  border: 1px solid #363a45;
  border-radius: 4px;
  color: #d1d4dc;
  font-size: 12px;
  padding: 4px 8px;
  cursor: pointer;
}

.width-input {
  width: 40px;
  background: #2a2e39;
  border: 1px solid #363a45;
  border-radius: 4px;
  color: #d1d4dc;
  font-size: 12px;
  padding: 4px 6px;
  text-align: center;
}

.param-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
}

.param-label {
  font-size: 13px;
  color: #d1d4dc;
}

.param-input {
  width: 80px;
  background: #2a2e39;
  border: 1px solid #363a45;
  border-radius: 4px;
  color: #d1d4dc;
  font-size: 13px;
  padding: 6px 10px;
  text-align: center;
}

.param-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.settings-footer {
  padding: 12px 16px;
  border-top: 1px solid #2a2e39;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.settings-btn {
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  border: none;
}

.settings-btn.reset {
  background: transparent;
  color: #787b86;
}

.settings-btn.reset:hover {
  color: #d1d4dc;
}

.settings-btn.cancel {
  background: #363a45;
  color: #d1d4dc;
}

.settings-btn.cancel:hover {
  background: #434754;
}

.settings-btn.confirm {
  background: #2962ff;
  color: #fff;
}

.settings-btn.confirm:hover {
  background: #1e53e4;
}

/* SMC 设置样式 */
.smc-element-section {
  margin-top: 12px;
  padding: 10px;
  background: rgba(42, 46, 57, 0.3);
  border-radius: 6px;
}

.smc-element-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.smc-checkbox {
  display: flex;
  align-items: center;
  margin-right: 8px;
}

.smc-checkbox input[type="checkbox"] {
  width: 14px;
  height: 14px;
  cursor: pointer;
  margin: 0;
}

.smc-label {
  font-size: 12px;
  font-weight: 500;
  position: relative;
}

.fvg-label { color: #4CAF50; }
.reference-label { color: #FFD700; }
.ob-label { color: #00D9FF; }
.swing-label { color: #00D9FF; }
.bos-label { color: #FFD700; }
.choch-label { color: #9C27B0; }

.label-hint {
  font-size: 9px;
  font-weight: 400;
  color: #787b86;
  margin-left: 4px;
  cursor: help;
  position: relative;
}

.label-hint[title] {
  position: absolute;
  left: 100%;
  background: rgba(0, 0, 0, 0.9);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  white-space: nowrap;
  z-index: 10;
  pointer-events: auto;
  opacity: 0;
  transform: translateY(0);
  transition: opacity 0.3s, opacity 0.3s, transform 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.smc-description {
  margin-top: 12px;
  padding: 8px 12px;
  background: rgba(33, 150, 243, 0.2);
  border-radius: 4px;
  font-size: 11px;
}

.desc-item {
  margin: 4px 0;
  color: #a0aeb0;
}

.desc-item strong {
  color: inherit;
}

.smc-element-controls {
  padding-left: 22px;
  margin-top: 8px;
}

.control-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 0;
}

.control-label {
  font-size: 11px;
  color: #787b86;
  min-width: 60px;
}

.color-input.small {
  width: 24px;
  height: 24px;
}

.opacity-slider {
  width: 80px;
  height: 4px;
  -webkit-appearance: none;
  background: #2a2e39;
  border-radius: 2px;
  outline: none;
}

.opacity-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 12px;
  height: 12px;
  background: #2962ff;
  border-radius: 50%;
  cursor: pointer;
}

.opacity-value {
  font-size: 10px;
  color: #787b86;
  min-width: 30px;
  text-align: right;
}

.count-input {
  width: 50px;
  background: #2a2e39;
  border: 1px solid #363a45;
  border-radius: 4px;
  color: #d1d4dc;
  font-size: 11px;
  padding: 4px 6px;
  text-align: center;
}

/* 区域设置样式 */
.area-setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #2a2e39;
}

.area-setting-row:last-of-type {
  border-bottom: none;
}

.area-label {
  font-size: 12px;
  color: #d1d4dc;
  min-width: 120px;
}

.area-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.area-controls .opacity-slider {
  width: 70px;
}

.alert-line-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  margin-top: 5px;
  border-top: 1px solid #2a2e39;
}

.alert-line-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.alert-line-checkbox input[type="checkbox"] {
  width: 14px;
  height: 14px;
  cursor: pointer;
  margin-right: 8px;
}

.checkbox-label {
  font-size: 12px;
  color: #d1d4dc;
}
</style>
