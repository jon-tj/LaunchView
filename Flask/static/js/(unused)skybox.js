
const sides = ["ft", "bk", "up", "dn", "rt", "lf"];

function loadSkybox(skybox="space"){
    var basePath = "../static/img/skybox/";
    var baseFilename = basePath + skybox;
    var fileType = ".png";
    var pathStings = sides.map(side => {
        return baseFilename + "_" + side + fileType;
    });

    const materialArray = pathStings.map(image => {
        let texture = new THREE.TextureLoader().load(image);
        return new THREE.MeshBasicMaterial({ map: texture, side: THREE.BackSide });
    });
        
    var skyboxGeo = new THREE.BoxGeometry(1000, 1000, 1000);
    var box = new THREE.Mesh(skyboxGeo,materialArray);
    return box
}

scene.add(loadSkybox())