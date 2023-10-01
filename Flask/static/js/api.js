function getAll(){
    fetch("/api/gps")
    .then(r=>r.json())
    .then(obj=>{
        if(obj.err){
            
        }
    });
}