import * as THREE from 'three'

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const scene = new THREE.Scene();
const canvas = document.getElementById("viscanv")
const width = canvas.style.width.slice(0, -2)
const height = canvas.style.height.slice(0, -2)
const camera = new THREE.PerspectiveCamera(75, width/height, 0.1, 1000)
const renderer = new THREE.WebGLRenderer()
renderer.setSize(width, height)
canvas.append(renderer.domElement)
camera.position.set(2, 2, 2)
camera.lookAt(0, 0, 0)
scene.add(new THREE.AxesHelper(1000))
const light = new THREE.AmbientLight(0xffffff, 10)
scene.add(light)
const planeGeometry = new THREE.PlaneGeometry(10, 10, 30, 30)
const planeMaterial = new THREE.MeshBasicMaterial({
    color: 0xffff00,
    side: THREE.DoubleSide,
    wireframe: true
})
const plane = new THREE.Mesh(planeGeometry, planeMaterial)
plane.rotateX(Math.PI/2)
scene.add(plane)
const micDir = new THREE.Vector3(0, 0, 1)
const mic = new THREE.Vector3(0, 0, 0)
const arrowHelper = new THREE.ArrowHelper(micDir, mic, 1, 0xff00ff)
scene.add(arrowHelper)

async function render() {
    requestAnimationFrame(render)
    renderer.render(scene, camera)
}

async function loop() {
    while (document.hasFocus()) {
        const h = document.getElementById("microphone-height").value
        const micX = document.getElementById("mic-direction-x").value
        const micY = document.getElementById("mic-direction-y").value
        const micZ = document.getElementById("mic-direction-z").value
        const micDir = new THREE.Vector3(micX, micY, micZ)
        arrowHelper.setDirection(micDir)
        plane.position.set(0, -h, 0)
        render().then()
        await sleep(5)
    }
}

loop().then()



