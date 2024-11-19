<template>
  <div
    v-if="isVisible"
    class="floating-window"
    :style="{ width: windowWidth + 'px', height: windowHeight + 'px', top: windowTop + 'px', left: windowLeft + 'px' }"
    ref="window"
    @mousedown="startDrag"
    @mouseup="stopDrag"
    @mousemove="dragWindow"
  >
    <div class="header">
      <img src="@/assets/logo.png" alt="Logo" class="window-logo me-2" />
      <span class="title h4 mb-0">{{ title }}</span>  
      <button @click="closeWindow" class="close-btn">×</button>
    </div>
    <div class="content">
      <slot></slot> <!-- 插入其他组件的地方 -->
    </div>
    <div class="resize-handle" @mousedown="startResize"></div>
  </div>
</template>
  
<script>
export default {
  name: "FloatingWindow",
  props: {
    title: {
      type: String,
      required: true,
      default: '窗口'
    }
  },
  data() {
    return {
      isVisible: true,
      isDragging: false,
      isResizing: false,
      windowTop: 50,
      windowLeft: 50,
      windowWidth: 500,
      windowHeight: 560,
      dragStartX: 0,
      dragStartY: 0,
      resizeStartWidth: 0,
      resizeStartHeight: 0,
      resizeStartX: 0,
      resizeStartY: 0
    };
  },
  methods: {
    startDrag(event) {
      if (event.target === this.$refs.window || event.target === this.$refs.window.querySelector('.header')) {
        this.isDragging = true;
        this.dragStartX = event.clientX;
        this.dragStartY = event.clientY;
      }
    },
    stopDrag() {
      this.isDragging = false;
    },
    dragWindow(event) {
      if (this.isDragging) {
        const deltaX = event.clientX - this.dragStartX;
        const deltaY = event.clientY - this.dragStartY;
        this.windowLeft += deltaX;
        this.windowTop += deltaY;
        this.dragStartX = event.clientX;
        this.dragStartY = event.clientY;
      }
    },
    closeWindow() {
      this.isVisible = false;
    },
    startResize(event) {
      this.isResizing = true;
      this.resizeStartX = event.clientX;
      this.resizeStartY = event.clientY;
      this.resizeStartWidth = this.windowWidth;
      this.resizeStartHeight = this.windowHeight;
      event.preventDefault(); // 防止文本选择等默认行为
    },
    resizeWindow(event) {
      if (this.isResizing) {
        const deltaX = event.clientX - this.resizeStartX;
        const deltaY = event.clientY - this.resizeStartY;
        this.windowWidth = this.resizeStartWidth + deltaX;
        this.windowHeight = this.resizeStartHeight + deltaY;
      }
    },
    stopResize() {
      this.isResizing = false;
    }
  },
  mounted() {
    window.addEventListener('mousemove', this.resizeWindow);
    window.addEventListener('mouseup', this.stopResize);
  },
  beforeUnmount() {
    window.removeEventListener('mousemove', this.resizeWindow);
    window.removeEventListener('mouseup', this.stopResize);
  }
};
</script>
  
<style scoped>
.floating-window {
  position: absolute;
  background-color: rgba(255, 255, 255, 0.9); /* 半透明背景 */
  border-radius: 8px; /* 圆角 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); /* 柔和阴影 */
  overflow: hidden;
  z-index: 1000;
  /* Add text selection prevention */
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background-color: #3d3f42;
  color: white;
  font-size: 16px;
  font-weight: 500;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  cursor: move;
}

.title {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: white;
  cursor: pointer;
}

.content {
  padding: 0px;
  height: calc(100% - 40px); /* 留出空间给header */
}

.resize-handle {  /* 调整大小的手柄 */
  position: absolute;
  right: 0;
  bottom: 0;
  width: 16px;
  height: 16px;
  cursor: se-resize;
  background-color: transparent;
  border-radius: 0 0 8px 0;
}

.window-logo {
width: 30px;  /* 缩小固定宽度 */
height: 30px; /* 缩小固定高度 */
object-fit: contain;
transition: transform 0.2s;
margin-right: 8px;
}

/* 确保在小屏幕上不会太大 */
@media (max-width: 768px) {
.window-logo {
width: 16px;
height: 16px;
}
}

.title {
font-size: 1.25rem;  /* 20px */
font-weight: 500;
margin: 0 10px;
color: white;
}
</style>
  