(function(e){
	var api = {};
	e.simplecanvas=api;
	var W = null;
	var H = null;
    var OW = null;
    var OH = null;
	var canvas = null;
	var context = null;
	var rawData = null;
	api.init = function(width, height, divId) {
		canvas = document.createElement('canvas');
		canvas.style.border = "1px solid grey";
		W = width;
		H = height;
		canvas.width = width;
		canvas.height = height;
		var parentDiv = document.getElementById(divId);
		parentDiv.appendChild(canvas);
        /*
		var p = document.createElement('p');
		p.id = 'simplecanvs_fps';
		parentDiv.appendChild(p)
        */
		context = canvas.getContext('2d');
        context.imageSmoothingEnabled= false;

	};
	api.putpixel = function(x, y, c) {
		//x = Math.floor(x);
		//y = Math.floor(y);
		x = x>>0;
		y = y>>0;
		/*
		var p = x+y*W;
		p *= 4;
		rawData.data[p + 0] = r;
		rawData.data[p + 1] = g;
		rawData.data[p + 2] = b;
		rawData.data[p + 3] = a;
		*/
		//if (a == undefined) a = 255;
		//context.fillStyle = 'rgba(' + r + ',' + g + ',' + b + ',' + (a / 255) + ')';
		//if (c.length == 3)
			//context.strokeStyle = 'rgb(' + c + ')';
		//else
			//context.strokeStyle = 'rgba(' + c + ')';
		if (c.length == 3)
			context.fillStyle = 'rgb(' + c + ')';
		else
			context.fillStyle = 'rgba(' + c + ')';
		context.fillRect(x,y,1,1);
		//context.moveTo(x,y);
		//context.lineTo(x+1,y);
	};
	api.putrectangle = function(x, y, w, h, c) {
		//x = Math.floor(x);
		//y = Math.floor(y);
		x = x>>0;
		y = y>>0;
		w = w>>0;
		h = h>>0;
		/*
		var p = x+y*W;
		p *= 4;
		rawData.data[p + 0] = r;
		rawData.data[p + 1] = g;
		rawData.data[p + 2] = b;
		rawData.data[p + 3] = a;
		*/
		//if (a == undefined) a = 255;
		if (c.length == 3)
            context.fillStyle = 'rgb(' + c + ')';
		else
            context.fillStyle = 'rgba(' + c + ')';
		context.fillRect(x,y,w,h);
	};
	api.run = function(f) {
		context.beginPath();
		f();
		context.stroke();
	};

var onEachFrame;

if (window.requestAnimationFrame) {
  onEachFrame = function(cb) {
    var _cb,
      _this = this;
    _cb = function() {
      cb();
      return window.requestAnimationFrame(_cb);
    };
    return _cb();
  };
} else if (window.webkitRequestAnimationFrame) {
  onEachFrame = function(cb) {
    var _cb,
      _this = this;
    _cb = function() {
      cb();
      return window.webkitRequestAnimationFrame(_cb);
    };
    return _cb();
  };
} else if (window.mozRequestAnimationFrame) {
  onEachFrame = function(cb) {
    var _cb,
      _this = this;
    _cb = function() {
      cb();
      return window.mozRequestAnimationFrame(_cb);
    };
    return _cb();
  };
} else {
  onEachFrame = function(cb) {
    return setInterval(cb, 1000 / 60);
  };
}


	api.load_image = function(url) {
		var img = new Image();
		img.src = url;
		return img;
	}
	api.draw_image = function(x,y,img) {
		context.drawImage(img, Math.floor(x), Math.floor(y));
	}
	api.text = function(x,y,text,size,c) {
		context.fillStyle = "rgb("+c+")";
		context.font = size+"px";
		context.fillText(text, Math.floor(x), Math.floor(y));
	}
	api.clear = function(c) {
		if (c)
		{
			context.fillStyle = "rgb("+c+")";
			context.fillRect(0,0,W,H);
		}
		else
			context.clearRect(0,0,W,H);
	}

	api.onkeydown = function(f) {
		document.onkeydown = function(e) {
			f(e.keyCode);
		}
	}

	api.mainloop = function(f) {
		onEachFrame(function(){
            var force_redraw = false;
            if (OW != $(canvas).width() || OH != $(canvas).height()) {
                OW = $(canvas).width();
                OH = $(canvas).height();
                /*
                canvas.width = OW;
                canvas.height = OH;
                octx = context;
                //context = canvas.getContext('2d');
                context.scale(canvas.width/W, canvas.height/H);
                console.log(OW, OH, W, H, canvas.width/W, canvas.height/H);
                */
                force_redraw = true;
            }
			//var t = (new Date).getTime();
			context.beginPath();
			f(force_redraw);
			context.stroke();
			//var t2 = (new Date).getTime();
//$("#simplecanvs_fps").text((t2-t) + ' ' + (pxcnt-oldpxcnt));
		});
	}
})(window);
