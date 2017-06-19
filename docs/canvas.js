var canvas = document.querySelector('canvas');
var c = canvas.getContext('2d');

canvas.width = innerWidth;
canvas.height = innerHeight;

addEventListener('resize',  function() {
	canvas.width = innerWidth;
	canvas.height = innerHeight;

	init();
});

function rand(min, max) {
	return Math.floor(Math.random() * (max - min + 1) + min);
}

function randColor() {
    var colors = ['#fad250','#fde7a3','#fdc806'];
	return colors[Math.floor(Math.random() * colors.length)];
}

function Circle(x, y, r, color) {
	this.x = x;
	this.y = y;
	this.r = r;
	this.color = color;

	this.update = function() {
        if(this.y < -this.r ) {
            this.x = rand(this.r, canvas.width - this.r);
            this.y = canvas.height + this.r;
        }
        this.x += rand(-1,1);
        this.y += rand(-3,2);
		this.draw();
	};

	this.draw = function() {
		c.beginPath();
		c.arc(this.x, this.y, this.r, 0, Math.PI * 2, false);
		c.fillStyle = this.color;
		c.fill();
		c.closePath();
	};
}

var circles;
function init() {
    circles = [];
    for(var i = 0; i < rand(30, 60); i++) {
        var r  = rand(5, 25);
        var x  = rand(r, canvas.width - r);
        var y  = rand(0, canvas.height - r);
        circles.push(new Circle(x, y, r, randColor()));
    }
}

function animate() {
	requestAnimationFrame(animate);
	c.clearRect(0, 0, canvas.width, canvas.height);
    for (var i = 0; i < circles.length; i++) circles[i].update();
}

init();
animate();
