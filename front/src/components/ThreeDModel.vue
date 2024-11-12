<template>
  <div id="threeDModel"></div>
</template>

<script>
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";

export default {
  name: "ThreeDModel",
  mounted() {
    this.$nextTick(() => {
      this.initScene();
      window.addEventListener("resize", this.onWindowResize);
    });
  },
  beforeUnmount() {  
    window.removeEventListener("resize", this.onWindowResize);
    if (this.renderer) {
      this.renderer.dispose();
    }
  },
  methods: {
    initScene() {
      // 创建场景
      this.scene = new THREE.Scene();

      // 设置相机
      const width = window.innerWidth;
      const height = window.innerHeight;
      this.camera = new THREE.PerspectiveCamera(60, width / height, 1, 100000);
      this.camera.position.set(0,100,100);
      this.camera.lookAt(this.scene.position);

      // 创建渲染器
      const container = document.getElementById("threeDModel");
      this.renderer = new THREE.WebGLRenderer({ alpha: true });
      this.renderer.setSize(container.clientWidth, container.clientHeight);
      container.appendChild(this.renderer.domElement);

      // 添加光源
      const pointLight = new THREE.PointLight(0xffffff);
      pointLight.position.set(500, 500, 500);
      this.scene.add(pointLight);

      const ambientLight = new THREE.AmbientLight(0x888888);
      this.scene.add(ambientLight);

      // 添加 OrbitControls
      this.controls = new OrbitControls(this.camera, this.renderer.domElement);

      // 加载 GLTF 模型
      const loader = new GLTFLoader();
      loader.load("models/glTF/Lantern.gltf", (gltf) => {
        this.scene.add(gltf.scene);
        console.log("ThreeDModel mounted");
      },
      undefined,
      (error) => {
        console.error(error);
      });
      

      // 开始渲染循环
      this.render();
    },
    render() {
      this.renderer.render(this.scene, this.camera);
      requestAnimationFrame(this.render.bind(this)); // 请求帧更新渲染
    },
    onWindowResize() {
      const width = window.innerWidth;
      const height = window.innerHeight;
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(width, height);
    },
  },
};
</script>

<style scoped>
#threeDModel {
  width: 100%;
  height: 100%; /* 改为百分比，适应 FloatWindow */
  background-color: rgba(0, 0, 0, 0.5); /* 半透明背景 */
}
</style>