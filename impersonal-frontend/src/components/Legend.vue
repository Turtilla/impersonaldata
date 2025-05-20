<template>
    <div
      class="draggable-legend"
      :style="{ top: pos.y + 'px', left: pos.x + 'px' }"
      @mousedown="startDrag"
    >
      <span class="text-2xl font-header">Legend</span>
      <svg :width="width" :height="legendHeight">
        <g
          v-for="(item, index) in categories"
          :key="item.category"
          :transform="`translate(0, ${index * rowHeight})`"
        >
          <rect
            :x="0"
            :y="0"
            :width="colorBoxSize"
            :height="colorBoxSize"
            :fill="item.color"
          />
          <text
            :x="colorBoxSize + 10"
            :y="colorBoxSize * 0.75"
            font-size="14"
            fill="#000"
          >
            {{ formatLabel(item.category) }}
          </text>
        </g>
      </svg>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, computed } from 'vue'
  
  interface Category {
    category: string
    color: string
  }
  
  const categories = ref<Category[]>([])
  const width = 200
  const rowHeight = 24
  const colorBoxSize = 16
  
  const formatLabel = (label: string) =>
    label//label.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())
  
  const fetchData = async () => {
    const response = await fetch('/config.json')
    const data = await response.json()
    categories.value = data.categories.sort((a: Category, b: Category) =>
      formatLabel(a.category).localeCompare(formatLabel(b.category))
    )
  }

  onMounted(fetchData)
  
  const legendHeight = computed(() => categories.value.length * rowHeight)
  
  // --- Drag behavior ---
  const pos = ref({ x: 50, y: 150 })
  const dragging = ref(false)
  const offset = ref({ x: 0, y: 0 })
  
  const startDrag = (e: MouseEvent) => {
    dragging.value = true
    offset.value = {
      x: e.clientX - pos.value.x,
      y: e.clientY - pos.value.y
    }
    document.addEventListener('mousemove', drag)
    document.addEventListener('mouseup', stopDrag)
  }
  
  const drag = (e: MouseEvent) => {
    if (!dragging.value) return
    pos.value = {
      x: e.clientX - offset.value.x,
      y: e.clientY - offset.value.y
    }
  }
  
  const stopDrag = () => {
    dragging.value = false
    document.removeEventListener('mousemove', drag)
    document.removeEventListener('mouseup', stopDrag)
  }
  </script>
  
  <style scoped>
  .draggable-legend {
    position: absolute;
    z-index: 999;
    cursor: move;
    user-select: none;
    background-color: white;
    border: 1px solid #ccc;
    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
    padding: 8px;
    border-radius: 8px;
  }
  </style>
  