<template>
    <div v-show="visible" class="first-person-container">
        <div id="first-person-map" class="first-person-map"></div>
    </div>
</template>

<script>
import mapboxgl from 'mapbox-gl'

export default {
    name: 'FirstPersonView',
    props: {
        visible: {
            type: Boolean,
            default: false
        },
        mainMap: {
            type: Object,
            required: true
        }
    },
    data() {
        return {
            map: null,
            syncedLayers: new Set(), // 用于跟踪已同步的图层
        }
    },
    mounted() {
        // 等待主地图加载完成
        if (this.mainMap && this.mainMap.loaded()) {
            this.initMap()
        } else {
            // 如果主地图还没加载完成，等待load事件
            this.mainMap?.once('load', () => {
                this.initMap()
            })
        }
    },
    methods: {
        initMap() {
            if (!this.mainMap) return

            mapboxgl.accessToken = 'pk.eyJ1IjoiYWlsYW56aGFuZyIsImEiOiJjbTMycjh3b28xMXg0MmlwcHd2ZmttZWYyIn0.T42ZxSkFvc05u3vfMT6Paw';

            const center = this.mainMap.getCenter()

            this.map = new mapboxgl.Map({
                container: 'first-person-map',
                style: 'mapbox://styles/mapbox/light-v11',
                center: center,
                zoom: 17,
                pitch: 90,
                bearing: 0,
                attributionControl: false
            })

            // 等待小地图加载完成后再添加事件监听和同步图层
            this.map.on('load', () => {
                this.mainMap.on('move', this.syncWithMainMap)
                
                // 同步现有的geojson图层
                this.syncExistingLayers()
                
                // 监听新图层的添加
                this.mainMap.on('sourcedata', this.handleNewLayers)
            })
        },

        syncExistingLayers() {
            const layers = this.mainMap.getStyle().layers
            layers.forEach(layer => {
                if (this.isGeoJSONLayer(layer)) {
                    this.syncLayer(layer.id)
                }
            })
        },

        handleNewLayers(e) {
            if (e.dataType === 'source' && e.isSourceLoaded) {
                const layers = this.mainMap.getStyle().layers
                layers.forEach(layer => {
                    if (this.isGeoJSONLayer(layer) && !this.syncedLayers.has(layer.id)) {
                        this.syncLayer(layer.id)
                    }
                })
            }
        },

        isGeoJSONLayer(layer) {
            if (!layer.source) return false
            const source = this.mainMap.getSource(layer.source)
            return source && source.type === 'geojson'
        },

        syncLayer(layerId) {
            if (this.syncedLayers.has(layerId)) return

            const layer = this.mainMap.getStyle().layers.find(l => l.id === layerId)
            if (!layer) return

            const sourceId = layer.source
            const source = this.mainMap.getSource(sourceId)
            
            // 添加数据源
            if (!this.map.getSource(sourceId)) {
                this.map.addSource(sourceId, {
                    type: 'geojson',
                    data: source._data
                })
            }

            // 添加图层
            if (!this.map.getLayer(layerId)) {
                const layerDef = {...layer}
                this.map.addLayer(layerDef)
            }

            // 监听源数据更新
            this.mainMap.on(`sourcedata`, (e) => {
                if (e.sourceId === sourceId && e.isSourceLoaded && this.map.getSource(sourceId)) {
                    const updatedData = this.mainMap.getSource(sourceId)._data
                    this.map.getSource(sourceId).setData(updatedData)
                }
            })

            this.syncedLayers.add(layerId)
        },

        syncWithMainMap() {
            if (!this.map || !this.mainMap) return
            
            const center = this.mainMap.getCenter()
            this.map.setCenter(center)
        }
    },
    beforeUnmount() {
        if (this.mainMap) {
            this.mainMap.off('move', this.syncWithMainMap)
            this.mainMap.off('sourcedata', this.handleNewLayers)
        }
        if (this.map) {
            this.map.remove()
        }
    },
    watch: {
        visible(newVal) {
            if (newVal) {
                this.$nextTick(() => {
                    if (this.map) {
                        this.map.resize()
                        this.syncWithMainMap()
                    }
                })
            }
        },
        // 监听mainMap的变化
        mainMap: {
            handler(newMap) {
                if (newMap && !this.map) {
                    if (newMap.loaded()) {
                        this.initMap()
                    } else {
                        newMap.once('load', () => {
                            this.initMap()
                        })
                    }
                }
            },
            immediate: true
        }
    }
}
</script>

<style scoped>
.first-person-container {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 320px;
    height: 240px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
    overflow: hidden;
    z-index: 1000;
}

.first-person-map {
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
}
</style>