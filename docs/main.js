var t;

window.onload = function() {
    t = document.querySelector('.textField');
};

document.querySelector('.youtubeUrl').addEventListener('keypress', function(event) {
    if(this.classList.contains('invalid')) {
        document.querySelector('.xout').remove();
        this.classList.remove('invalid');
    }
    if(event.keyCode == 13) {
        getVid(this.value);
    }
});

/*----------------------------------------------------------------*/

function checkText(e) {
    var text = t.value;
    if(e.keyCode == 13) {
        saveText(text);
    }

    if(e.keyCode != 8) {
        var a = String.fromCharCode(e.which || e.keyCode);
        var validKey = /[1234aefnpsw]/;
        if(!validKey.test(a)) {
            e.preventDefault();
            return false;
        }
    }

    if(text.length >= 45) {
        t.style.fontSize = '20px';
    } else {
        t.style.fontSize = '40px';
    }
}

function saveText(v) {
    if(v.length > 0) {
        var ul = document.querySelector('.savedText');
        var new_li = document.createElement('li');

        /*var new_type = document.createElement('i');
        new_type.classList.add('material-icons');
        new_type.classList.add('timeStamp');
        new_type.innerHTML = '';*/

        var new_text = document.createElement('b');
        new_text.classList.add('pBp');
        new_text.innerHTML = v;

        var new_clear = document.createElement('i');
        new_clear.classList.add('material-icons');
        new_clear.classList.add('clear');
        new_clear.setAttribute('onclick', 'removeText(this.parentElement)');
        new_clear.innerHTML = '&#xE14C';

        //new_li.appendChild(new_type);
        new_li.appendChild(new_text);
        new_li.appendChild(new_clear);

        if(ul.hasChildNodes()) {
            var fC = ul.firstChild;
            ul.insertBefore(new_li, fC);
        } else {
            document.querySelector('.savedTextArea h2').remove();
            ul.appendChild(new_li);
        }
    }

    t.value = '';
}

/*----------------------------------------------------------------*/

function removeText(el) {
    el.remove();

    var ul = document.querySelector('.savedText');

    if(!ul.hasChildNodes()) {
        var placeHolder = document.createElement('h2');
        var area = document.querySelector('.savedTextArea');

        placeHolder.innerHTML = 'Play by Play';
        area.appendChild(placeHolder);
    }
}

/*----------------------------------------------------------------*/

function reset() {
    var ul = document.querySelector('.savedText');

    if(ul.hasChildNodes()) {
        ul.innerHTML = '';

        var placeHolder = document.createElement('h2');
        var area = document.querySelector('.savedTextArea');

        placeHolder.innerHTML = 'Play by Play';
        area.appendChild(placeHolder);
    }

    t.value = '';
}

function download() {
    var pBp = Array.prototype.slice.call(document.querySelectorAll('.pBp')).reverse();
    for (var i = 0; i < pBp.length; i++) {pBp[i] = pBp[i].valueOf().textContent;}
    if(t.value !== '') {
        pBp.push(t.value);
    }

    if(pBp.length > 0) {
        var link = document.createElement('a');
        link.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(pBp.join('\n')));
        link.setAttribute('download', 'datasheet.txt');

        var e = document.createEvent('MouseEvents');
        e.initEvent('click', true, false);

        link.dispatchEvent(e);
    }
}

/*----------------------------------------------------------------*/

function deleteText() {
    document.querySelector('.invalid').value = '';
    document.querySelector('.youtubeUrl').classList.remove('invalid');
    document.querySelector('.xout').remove();
}

function getVid(url) {
    var correctedUrl;
    var valid;
    var input = document.querySelector('.youtubeInput');

    if(new RegExp('https://www.youtube.com/watch?').test(url)) {
        correctedUrl = url.replace('watch?v=', 'embed/');
        valid = true;
    } else if(new RegExp('https://www.youtube.com/embed').test(url)) {
        correctedUrl = url;
        valid = true;
    } else if(new RegExp('https://www.youtube.com/').test(url)) {
        correctedUrl = url.replace('.com/', '.com/embed/');
        valid = true;
    } else {
        valid = false;
    }

    if(valid) {
        document.querySelector('.youtubeUrl').classList.remove('invalid');
        input.remove();

        var video = document.createElement('iframe');
        video.classList.add('youtubeVid');
        video.setAttribute('src', correctedUrl);
        video.setAttribute('frameborder', '0');

        var container = document.querySelector('.youtubeBox');
        container.appendChild(video);
    } else {
        document.querySelector('.youtubeUrl').classList.add('invalid');

        var del_BTN = document.createElement('i');
        del_BTN.classList.add('material-icons');
        del_BTN.classList.add('xout');
        del_BTN.setAttribute('onclick', 'deleteText()');
        del_BTN.innerHTML = '&#xE5C9';
        input.appendChild(del_BTN);
    }
}

/*----------------------------------------------------------------*/
