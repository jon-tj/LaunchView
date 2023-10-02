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
        switch(countdown.timeRemaining){
            case 180: say("3 minutes till launch"); break;
            case 60: say("1 minute till launch"); break;
            case 30: say("30 seconds"); break;
            case 10: say("10 seconds"); break;
            case 5: say("5 seconds"); break;
            case 4: say("4 seconds"); break;
            case 3: say("3 seconds"); break;
            case 2: say("2 seconds"); break;
            case 1: say("1 second"); break;
            case 0:
                say("liftoff")
                fetch("/api/fire");
                break;
        }
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