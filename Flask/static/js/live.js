
// Maybe consider rendering live boxplots for data summarization?
function setupGraph(name,color="cyan"){
    var g=new Graph(document.querySelector("canvas#"+name),color,30,name)
        .setValues([1,2,3,2,5,1,3,2,0.4,5,20,12,13,12,14,12,10,9,7,10,7]) //dummy values
    g.render()
    return g
}
const gRSSI=setupGraph("RSSI","pink")
const gTemp=setupGraph("Temperature","#FF7F64")
const gVel=setupGraph("Velocity","#77FF64")
// Test the live rendering!
/*setInterval(() => {
    for(var i=0; i<3; i++){
        gRSSI.appendValue(Math.random()*50)
        gTemp.appendValue(Math.random()*50)
    }
    gRSSI.render()
    gTemp.render()
}, 500);*/