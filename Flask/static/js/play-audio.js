const audioPlayers =[
    document.getElementById("tts1"),
    document.getElementById("tts2")
]
var lastPlayer=0
function say(message){
    lastPlayer++;
    lastPlayer%=2;
    audioPlayers[lastPlayer].src="../static/tts/"+message+".wav"
    setTimeout(()=>{
        audioPlayers[lastPlayer].play();
    },200)
}