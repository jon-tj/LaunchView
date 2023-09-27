
import * as THREE from 'three';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const scene = new THREE.Scene()
scene.background=new THREE.Color(0x6698e8)
scene.add(new THREE.AxesHelper(5))
scene.add(new THREE.AxesHelper(-5))

// dual-lit scene for EPICNESS
const sunlight = new THREE.DirectionalLight(0xccccff, 1);
sunlight.position.set(1, 1, 1);
scene.add(sunlight);
const sunlight1 = new THREE.DirectionalLight(0xffcccc, 1);
sunlight1.position.set(-1, -1, -1);
scene.add(sunlight1);

const camera = new THREE.PerspectiveCamera(
    60,
    window.innerWidth / window.innerHeight,
    1,
    1000
)
camera.position.z = 6

const renderer = new THREE.WebGLRenderer()
renderer.setSize(window.innerWidth, window.innerHeight)
document.body.appendChild(renderer.domElement)

const controls = new OrbitControls(camera, renderer.domElement)

const matRocket = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 0.5,
    metalness: 0.5
});

// creat the ground plane
const matGround = new THREE.MeshBasicMaterial({ color: 0x448833 });
const groundPlane = new THREE.Mesh(new THREE.PlaneGeometry(1000, 1000), matGround);
groundPlane.position.y=-4;
groundPlane.rotateX(-Math.PI/2);
scene.add(groundPlane);

// load the rocket
const loader = new STLLoader()
loader.load(
    '../static/models/rocket.stl',
    function (geometry) {
        const mesh = new THREE.Mesh(geometry, matRocket)
        mesh.scale.x=0.1
        mesh.scale.y=0.1
        mesh.scale.z=0.1
        scene.add(mesh)
    },undefined,
    (error) => {
        console.log(error)
    }
)

window.addEventListener('resize', onWindowResize, false)
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()
    renderer.setSize(window.innerWidth, window.innerHeight)
    render()
}

function animate() {
    requestAnimationFrame(animate)
    controls.update()
    render()
}

function render() {
    renderer.render(scene, camera)
}

animate()