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
        countdown.element.innerHTML=`${minutesRemaining}:${secondsRemaining}`
        
        if(countdown.timeRemaining==0) fetch("/api/fire")
    }
}, 1000);
function toggleCountdown(sender){
    countdown.enabled=!countdown.enabled;
    if(countdown.enabled)
        sender.innerHTML="Pause countdown"
    else sender.innerHTML="Start countdown"
}