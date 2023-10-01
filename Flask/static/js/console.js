const cli={
    log:document.getElementById("console-log"),
    input:document.getElementById("console-input"),
};
function executeCommand(){
    function trimLog(){
        while(cli.log.childElementCount>7){
            cli.log.removeChild(cli.log.firstChild);
        }
    }
    var q=cli.input.value;
    cli.log.innerHTML += `<p><span class="user"> ---- [User]</span> ${q}</p>`
    trimLog();
    cli.input.value="";
    q=q.toLowerCase();
    if(q.includes("nuke") && q.includes("orphanage")){
        cli.log.innerHTML += `<p><span class="system"> - [System]</span> Pranking orphans in progress...</p>`
        trimLog();
        setTimeout(() => {
            cli.log.innerHTML += `<p><span class="system"> - [System]</span> Prank complete.</p>`
            trimLog();
        }, 900);
        return;
    }
    fetch("/api/command",{
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({command:q})
    })
    .then(r=>r.json())
    .then(r=>{
        console.log(r);
        console.log(r.err==null)
        if(r.err!=null){
            cli.log.innerHTML += `<p><span class="system"> - [System]</span> <span class="err"> ${r.err}</span></p>`
        }else{
            cli.log.innerHTML += `<p><span class="system"> - [System]</span> ${r.value}</p>`
        }
        trimLog();
    });
}
cli.input.addEventListener("change", executeCommand)
cli.input.addEventListener("focus", (e)=>{cli.log.style.display="block"})
cli.input.addEventListener("focusout", (e)=>{cli.log.style.display="none"})