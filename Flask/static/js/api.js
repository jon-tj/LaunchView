function getAll(){
    fetch("/api/gps")
    .then(r=>r.json())
    .then(data=>{
        console.log(data)
    });
}