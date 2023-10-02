const countdown={
    timeRemaining: 60*10,
    element: document.getElementById("countdown"),
    enabled: false
}


setInterval(() => {
    if(countdown.enabled && countdown.timeRemaining>0){
        countdown.timeRemaining--;
        var minutesRemaining=Math.floor(countdown.timeRemaining/60);
        var secondsRemaining=countdown.timeRemaining-minutesRemaining*60;
        countdown.element.value=`${minutesRemaining}:${secondsRemaining}`;
        
        if(countdown.timeRemaining==0) fetch("/api/fire");
    }
}, 1000);
function toggleCountdown(sender){
    countdown.enabled=!countdown.enabled;
    if(countdown.enabled)
        sender.innerHTML="Pause countdown";
    else sender.innerHTML="Start countdown";
}
countdown.element.addEventListener("change",()=>{
    var s=countdown.element.value.split(":");
    var sec=parseInt(s[1])
    var min=parseInt(s[0])
    if(s.length==2 &! isNaN(sec) &! isNaN(min)){
        countdown.timeRemaining=min*60+sec;
        countdown.element.style.backgroundColor="transparent";
    }else{
        countdown.element.style.backgroundColor="red";
    }

});