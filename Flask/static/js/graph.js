
//helper functions
function remap(x,min1,max1,min2,max2){
    return (x-min1)/(max1-min1)*(max2-min2)+min2
}
function mean(X){
    var sum=0
    for(x of X) sum+=x
    return sum/X.length
}
function variance(X,mu=null){
    var sum=0
    if(mu==null) mu=mean(X)
    for(x of X)
        sum+=(x-mu)*(x-mu)
    return sum/X.length
}
function std(X,mu=null){
    if(mu==null) mu=mean(X)
    return Math.sqrt(variance(X,mu))
}

class Rect{
    constructor(x,y,w,h){
        this.x=x;
        this.y=y; // Note: y=bottom of rect
        this.w=w;
        this.h=h;
    }
    get bottom(){return this.y}
    get top(){return this.y+this.h}
    get left(){return this.x}
    get right(){return this.x+this.w}
}
class Graph{
    constructor(canvas,color,maxperiod,label="",lookback=10,dest=null,minY=null,maxY=null){
        this.canvas=canvas
        this.ctx=canvas.getContext("2d")
        this.color=color;
        if(dest==null){
            dest=new Rect(10,10,canvas.width-20,canvas.height-20)
        }
        this.dest=dest;
        this.maxperiod=maxperiod;
        this.minY=minY;
        this.maxY=maxY;
        this.lookback=lookback
        this.overlays={
            label:label,
            mean:false,
            confInt:true,
        }
        this.style={
            bgColor:"#eee"
        }
        this.values=[];
        this.tmean=[];
        this.tstd=[];
    }
    rolling(i=-1,window=-1){
        if(window==-1) window=this.lookback
        if(i<0) i+=this.values.length
        var arr=[]
        for(var j=Math.max(i-window,0); j<=i; j++)
            arr.push(this.values[j])
        return arr
    }
    appendValue(y){
        this.values.push(y)
        var window=this.rolling()
        this.tmean.push(mean(window))
        this.tstd.push(std(window))
    }

    recalcStats(){
        this.tmean.length=0
        this.tstd.length=0
        for(var i=0; i<this.values.length; i++){
            var window=this.rolling(i)
            this.tmean.push(mean(window))
            this.tstd.push(std(window))
        }
        
    }
    recalcDestRect(){
        this.dest=new Rect(10,10,this.canvas.width-20,this.canvas.height-20)
    }
    setValues(values){
        this.values=values;
        this.recalcStats()
        return this;
    }
    render(clear=true){
        if (clear){
            this.ctx.fillStyle=this.style.bgColor
            this.ctx.fillRect(0,0,this.canvas.width,this.canvas.height)
        }
        this.ctx.strokeStyle=this.color
        var minY=this.minY
        var maxY=this.maxY
        if(minY==null) minY=Math.min(...this.values)
        if(maxY==null) maxY=Math.max(...this.values)
        var i=Math.max(0,this.values.length-this.maxperiod);

        function pt(ths,i,render=true){
            var y=remap(ths.values[i],minY,maxY,ths.dest.top,ths.dest.bottom)
            var x=remap(i,ths.values.length,ths.values.length-ths.maxperiod,ths.dest.right-30,ths.dest.left)
            if(render) ths.ctx.lineTo(x,y)
            else ths.ctx.moveTo(x,y)
            return y
        }
        var lastY=0
        this.ctx.beginPath()
        pt(this,i++,false)
        for(; i<this.values.length; i++)
            lastY=pt(this,i)
        this.ctx.stroke()
    
        this.ctx.fillStyle=this.color
        this.ctx.font="18px Arial"
        this.ctx.fillText(this.values[this.values.length-1].toFixed(2),this.dest.right-40,lastY+5)

        if(this.overlays.mean){
            var mean=0
            for(var i=0; i<this.values.length; i++) mean+=this.values[i]
            mean/=this.values.length
            var y=remap(mean,minY,maxY,this.dest.top,this.dest.bottom)
            this.ctx.beginPath()
            this.ctx.moveTo(this.dest.left,y)
            this.ctx.lineTo(this.dest.right-50,y)
            this.ctx.stroke()
            this.ctx.fillText(mean.toFixed(2),this.dest.right-40,y+5)

        }
        if(this.overlays.label!=""){
            this.ctx.fillText(this.overlays.label,this.dest.x,this.dest.y+9,this.dest.w)
        }
        if(this.overlays.confInt){
            var upper=[]
            var lower=[]
            var X=[]
            var dy=this.dest.h/(maxY-minY)
            i=Math.max(0,this.values.length-this.maxperiod);
            function pt1(ths,i,render=true){
                var y=remap(ths.tmean[i],minY,maxY,ths.dest.top,ths.dest.bottom)
                upper.push(y+dy*ths.tstd[i])
                lower.push(y-dy*ths.tstd[i])
                var x=remap(i,ths.values.length,ths.values.length-ths.maxperiod,ths.dest.right-30,ths.dest.left)
                X.push(x)
                if(render) ths.ctx.lineTo(x,y)
                else ths.ctx.moveTo(x,y)
            }
            this.ctx.beginPath()
            pt1(this,i++,false)
            for(; i<this.values.length; i++)pt1(this,i)
            this.ctx.setLineDash([10, 10]);
            this.ctx.stroke()
            this.ctx.setLineDash([]);

            this.ctx.globalAlpha=0.1

            this.ctx.beginPath()
            for(var j=0; j<X.length; j++)
                this.ctx.lineTo(X[j],upper[j])
            for(var j=0; j<X.length; j++)
                this.ctx.lineTo(X[X.length-1-j],lower[X.length-1-j])

            this.ctx.closePath()
            this.ctx.fill()
            this.ctx.globalAlpha=1
        }
    }

}
