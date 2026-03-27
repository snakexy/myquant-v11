<template>
  <div class="drag-test">
    <h2>拖拽性能测试</h2>
    <div
      class="draggable-box"
      :style="{ left: box.x + 'px', top: box.y + 'px' }"
      @mousedown="startDrag">
      拖拽我
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const box = reactive({
  x: 100,
  y: 100,
  isDragging: false,
  offsetX: 0,
  offsetY: 0
})

const startDrag = (e) => {
  box.isDragging = true
  box.offsetX = e.clientX - box.x
  box.offsetY = e.clientY - box.y

  document.addEventListener('mousemove', handleDrag)
  document.addEventListener('mouseup', stopDrag)
}

const handleDrag = (e) => {
  if (!box.isDragging) return

  box.x = e.clientX - box.offsetX
  box.y = e.clientY - box.offsetY
}

const stopDrag = () => {
  box.isDragging = false
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
}
</script>

<style scoped>
.drag-test {
  position: relative;
  width: 100%;
  height: 100vh;
  background: #f0f0f0;
}

.draggable-box {
  position: absolute;
  width: 100px;
  height: 100px;
  background: #4CAF50;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  user-select: none;
  border-radius: 8px;
}

.draggable-box:active {
  cursor: grabbing;
}
</style>