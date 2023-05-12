import * as THREE from 'three'
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xdddddd)
const canvas = document.getElementById("viscanv")
const width = canvas.style.width.slice(0, -2)
const height = canvas.style.height.slice(0, -2)
const camera = new THREE.PerspectiveCamera(75, width/height, 0.1, 1000)
const renderer = new THREE.WebGLRenderer()

const controls = new OrbitControls(camera, renderer.domElement, scene)
controls.listenToKeyEvents(canvas)
controls.enableDamping = true
controls.dampingFactor = 0.05
controls.screenSpacePanning = false
controls.minDistance = 1
controls.maxDistance = 10

renderer.setSize(width, height)
canvas.append(renderer.domElement)
camera.position.set(2, 2, 2)
camera.lookAt(0, 0, 0)
scene.add(new THREE.AxesHelper(1000))
const light = new THREE.AmbientLight(0xffffff, 10)
scene.add(light)
const planeGeometry = new THREE.PlaneGeometry(10, 10, 100, 100)
const planeMaterial = new THREE.MeshBasicMaterial({
    color: 0xff00ff,
    side: THREE.DoubleSide,
    wireframe: true
})
const plane = new THREE.Mesh(planeGeometry, planeMaterial)
plane.rotateX(Math.PI/2)
scene.add(plane)
const micDir = new THREE.Vector3(0, 0, 1)
const mic = new THREE.Vector3(0, 0, 0)
const micArrow = new THREE.ArrowHelper(micDir, mic, 1, 0xffff00)
scene.add(micArrow)

async function render() {
    renderer.render(scene, camera)
}

async function animate() {
    const h = document.getElementById("microphone-height").value
    const micX = document.getElementById("mic-direction-x").value
    const micY = document.getElementById("mic-direction-y").value
    const micZ = document.getElementById("mic-direction-z").value
    const micDir = new THREE.Vector3(micX, micY, micZ)
    micArrow.setDirection(micDir)
    plane.position.set(0, -h, 0)
    requestAnimationFrame(animate)
    controls.update()
    render().then()
}

animate().then()