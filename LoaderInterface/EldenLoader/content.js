(function() {

    const REMOVE_DELAY = 5000;
    const FONT_URL = chrome.runtime.getURL("Agmena Pro Regular");
    const AUDIO_URL = chrome.runtime.getURL("elden_ring_sound.mp3");

    function playSound() {
        const audio = new Audio(AUDIO_URL);
        audio.volume = 0.6;

        const playPromise = audio.play();
        if (playPromise !== undefined) {
            playPromise.catch(error => {
                console.log("Elden Ring Sound blocked by browser policy:", error);
            });
        }
    }

    playSound();
    const style = document.createElement('style');
    style.textContent = `
        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            background: transparent;
            overflow: hidden;
            pointer-events: none;
        }

        @font-face {
            font-family: Agmena';
            src: url('${FONT_URL}') format('truetype');
        }

        #er-ui-container {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100%;
            height: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }

        .er-backing-bar {
            width: 100%;
            height: 100px;

            background: linear-gradient(
                rgba(0,0,0,0) 0%,
                rgba(0,0,0,0.8) 13%,
                rgba(0,0,0,0.8) 85%,
                rgba(0,0,0,0) 100%
            );

            -webkit-mask-image: linear-gradient(
                to bottom,
                transparent 0%,
                black 15%,
                black 85%,
                transparent 100%
            );
            mask-image: linear-gradient(
                to bottom,
                transparent 0%,
                black 15%,
                black 85%,
                transparent 100%
            );

            filter: blur(2px);

            opacity: 0;
            animation: barFadeIn 0.5s ease-out 0.5s forwards;
        }


        .er-souls-text {
            position: absolute;
            font-family: 'Agmena Pro Regular', serif;
            font-size: 4rem;

            padding: 0 2rem;
            text-transform: uppercase;
            white-space: nowrap;

            z-index: 10;

            background: #d8c472;
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;

            filter:
                drop-shadow(0 0 2px rgba(0,0,0,1.0))
                drop-shadow(0 0 10px rgba(212,191,105,0.5));

            opacity: 0;
            animation: textEntrance 3.5s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        }

        .er-souls-text::after {
            content: attr(data-text);

            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%) scale(1.0);
            background: none;
            -webkit-background-clip: border-box;
            background-clip: border-box;

            color: rgba(212, 191, 105, 0.15);

            z-index: -1;

            filter: blur(1px);
            white-space: nowrap;
            opacity: 0;
            animation: ghostExpand 4s cubic-bezier(0.1, 0.5, 0.1, 1) forwards;
        }

        @keyframes ghostExpand {
            0% {
                opacity: 0;
                transform: translate(-50%, -50%) scale(1.15);
                letter-spacing: 0.1em;
            }
            20% {
                opacity: 0.6;
            }
            100% {
                opacity: 1;
                transform: translate(-50%, -50%) scale(1.01);
                letter-spacing: 0.2em;
            }
        }

        #er-gl-canvas {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100%;
            height: 200px;
            z-index: -1;
            pointer-events: none;
            opacity: 0;
            animation: barFadeIn 1s ease-out forwards;
        }

        @keyframes textEntrance {
            0% { opacity: 0; transform: scale(1.2); letter-spacing: 0em; transform: scale(1.2, 1.2);}
            15% { opacity: 1; }
            100% { opacity: 1; transform: scale(1.0); letter-spacing: 0.05em; transform: scale(1.0, 1.0);}
        }

        @keyframes barFadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .er-fade-out {
            transition: opacity 1s ease;
            opacity: 0 !important;
        }

    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.id = 'er-ui-container';
    container.innerHTML = `
        <canvas id="er-gl-canvas"></canvas>
        <div class="er-backing-bar"></div>
        <h1 class="er-souls-text" data-text="NEW TAB OPENED">NEW TAB OPENED</h1>
    `;
    document.body.appendChild(container);

    const canvas = document.getElementById("er-gl-canvas");
    const gl = canvas.getContext("webgl", { alpha: true, premultipliedAlpha: false });

    if (!gl) return;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = 400;
    }
    window.addEventListener('resize', resize);
    resize();

    const vsSource = `attribute vec2 p; void main(){gl_Position=vec4(p,0.,1.);}`;
    const fsSource = `
        precision mediump float;
        uniform vec2 r;
        uniform float t;
        float rnd(vec2 s){return fract(sin(dot(s,vec2(12.9898,78.233)))*43758.5453);}
        float n(vec2 s){vec2 i=floor(s),f=fract(s);float a=rnd(i),b=rnd(i+vec2(1,0)),c=rnd(i+vec2(0,1)),d=rnd(i+vec2(1,1));vec2 u=f*f*(3.-2.*f);return mix(a,b,u.x)+(c-a)*u.y*(1.-u.x)+(d-b)*u.x*u.y;}
        float fbm(vec2 s){float v=0.,a=.5;for(int i=0;i<5;i++){v+=a*n(s);s*=2.;a*=.5;}return v;}
        void main(){
            vec2 uv=gl_FragCoord.xy/r.xy;
            vec2 s=uv; s.x*=r.x/r.y;
            vec2 q=vec2(fbm(s+0.1*t), fbm(s+vec2(1.)));
            vec2 k=vec2(fbm(s+q+vec2(1.7,9.2)+.15*t), fbm(s+q+vec2(8.3,2.8)+.126*t));
            float f=fbm(s+k);
            vec3 c=mix(vec3(.1,.05,0.),vec3(.8,.5,.2),clamp(f*f*4.,0.,1.));
            c=mix(c,vec3(1.,.9,.6),clamp(length(q),0.,1.));
            c=mix(c,vec3(1.),clamp(length(k.x),0.,1.));
            float ym=pow(1.-abs(uv.y-.5)*2.,3.);
            float xm=smoothstep(0.,.2,1.-abs(uv.x-.5)*2.);
            float a=(f*f+.5*f)*ym*xm;
            gl_FragColor=vec4(c*a*1.5,a);
        }
    `;

    const createShader = (type, src) => {
        const s = gl.createShader(type);
        gl.shaderSource(s, src);
        gl.compileShader(s);
        return s;
    };
    const p = gl.createProgram();
    gl.attachShader(p, createShader(gl.VERTEX_SHADER, vsSource));
    gl.attachShader(p, createShader(gl.FRAGMENT_SHADER, fsSource));
    gl.linkProgram(p);
    gl.useProgram(p);

    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,3,-1,-1,3]), gl.STATIC_DRAW);
    const pos = gl.getAttribLocation(p, "p");
    gl.enableVertexAttribArray(pos);
    gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 0, 0);

    const locR = gl.getUniformLocation(p, "r");
    const locT = gl.getUniformLocation(p, "t");
    const startT = performance.now();
    let frameId;

    function render() {
        if(!document.body.contains(canvas)) return;
        const now = (performance.now() - startT) * 0.001;
        gl.viewport(0, 0, canvas.width, canvas.height);
        gl.clearColor(0,0,0,0);
        gl.clear(gl.COLOR_BUFFER_BIT);
        gl.uniform2f(locR, canvas.width, canvas.height);
        gl.uniform1f(locT, now);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
        frameId = requestAnimationFrame(render);
    }
    render();

    setTimeout(() => {

        container.classList.add('er-fade-out');

        setTimeout(() => {
            if (frameId) cancelAnimationFrame(frameId);
            container.remove();
            style.remove();
        }, 1000);
    }, REMOVE_DELAY);

})();