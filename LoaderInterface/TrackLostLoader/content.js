(function() {
    const REMOVE_DELAY = 50000;
    const STRIPE_OFFSET_PX = 140;
    const AUDIO_TRACK_LOST = chrome.runtime.getURL("assets/track_fail.wav");
    const AUDIO_FAIL_FULL = chrome.runtime.getURL("assets/res_fail_full.ogg");
    const AUDIO_FAIL_LOOP = chrome.runtime.getURL("assets/res_fail_loop.ogg");

    const IMG_END_MID_F = chrome.runtime.getURL("assets/end_mid_f.png");
    const IMG_CLEAR_FAIL = chrome.runtime.getURL("assets/clear_fail.png");
    const IMG_STRIPE_TOP = chrome.runtime.getURL("assets/stripe_top.png");
    const IMG_STRIPE_BOTTOM = chrome.runtime.getURL("assets/stripe_bottom.png");
    const IMG_PAUSE_BG = chrome.runtime.getURL("assets/pausebg.png");

    let audioCtx = null;
    let masterGain = null;

    async function loadAudioBuffer(ctx, url) {
        const response = await fetch(url);
        const buffer = await response.arrayBuffer();
        return await ctx.decodeAudioData(buffer);
    }

    async function playSoundSequence() {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        audioCtx = new AudioContext();
        masterGain = audioCtx.createGain();
        masterGain.gain.value = 0.6;
        masterGain.connect(audioCtx.destination);

        try {
            const [b1, b2, b3] = await Promise.all([
                loadAudioBuffer(audioCtx, AUDIO_TRACK_LOST),
                loadAudioBuffer(audioCtx, AUDIO_FAIL_FULL),
                loadAudioBuffer(audioCtx, AUDIO_FAIL_LOOP)
            ]);

            const s1 = audioCtx.createBufferSource(); s1.buffer = b1;
            const s2 = audioCtx.createBufferSource(); s2.buffer = b2;
            const s3 = audioCtx.createBufferSource(); s3.buffer = b3; s3.loop = true;

            s1.connect(masterGain);
            s2.connect(masterGain);
            s3.connect(masterGain);

            const now = audioCtx.currentTime;
            s1.start(now);
            s2.start(now + b1.duration);
            s3.start(now + b1.duration + b2.duration);

        } catch (e) {
            console.error("Audio failed:", e);
        }
    }

    function fadeOutAudio(duration = 1) {
        if (!audioCtx || !masterGain) return;

        try {
            const now = audioCtx.currentTime;
            masterGain.gain.setValueAtTime(masterGain.gain.value, now);
            masterGain.gain.linearRampToValueAtTime(0, now + duration);
        } catch (e) {
            console.log("Fade out error", e);
        }
    }

    function cleanupAudio() {
        if (audioCtx) {
            if (audioCtx.state !== 'closed') audioCtx.close();
            audioCtx = null;
            masterGain = null;
        }
    }

    function showImageAndPlaySound() {
        playSoundSequence();

        const style = document.createElement('style');
        style.textContent = `
            #tracklost-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                z-index: 9999;
                pointer-events: none;
                overflow: hidden;
                font-size: 0;
            }

            .tl-group-3 {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 1;
                animation: tl-fade-in 0.8s ease-out forwards;
                opacity: 0;
            }
            .tl-group-3 img {
                width: 100%;
                height: 100%;
                object-fit: cover;
                transform: scale(1.2);
            }

            .tl-group-2 {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10;
                animation: tl-fade-in 0.8s ease-out forwards;
                opacity: 0;
            }
            .tl-stripe {
                position: absolute;
                left: 0;
                width: 100%;
                height: auto;
            }
            .tl-stripe-top {
                bottom: calc(50% + ${STRIPE_OFFSET_PX}px);
            }
            .tl-stripe-bottom {
                top: calc(50% + ${STRIPE_OFFSET_PX}px);
            }

            .tl-group-1 {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 20;
                display: flex;
                justify-content: center;
                align-items: center;
                animation: tl-pop-in-center 0.6s cubic-bezier(0.25, 1, 0.5, 1) forwards;
                opacity: 0;
            }

            .tl-img-end-mid { display: block; max-width: none; }
            .tl-img-clear-fail {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
            }

            @keyframes tl-fade-in {
                0% { opacity: 0; }
                100% { opacity: 1; }
            }
            @keyframes tl-pop-in-center {
                0% { opacity: 0; transform: translate(-50%, -50%) scale(1.5); }
                100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
            }

            #tracklost-container.fade-out {
                opacity: 0;
                transition: opacity 1s;
            }
        `;
        document.head.appendChild(style);
        const container = document.createElement('div');
        container.id = 'tracklost-container';
        const group3 = document.createElement('div'); group3.className = 'tl-group-3'; group3.innerHTML = `<img src="${IMG_PAUSE_BG}" alt="Background">`;
        const group2 = document.createElement('div'); group2.className = 'tl-group-2'; group2.innerHTML = `<img src="${IMG_STRIPE_TOP}" class="tl-stripe tl-stripe-top"><img src="${IMG_STRIPE_BOTTOM}" class="tl-stripe tl-stripe-bottom">`;
        const group1 = document.createElement('div'); group1.className = 'tl-group-1'; group1.innerHTML = `<img src="${IMG_END_MID_F}" class="tl-img-end-mid"><img src="${IMG_CLEAR_FAIL}" class="tl-img-clear-fail">`;
        container.appendChild(group3); container.appendChild(group2); container.appendChild(group1);
        document.body.appendChild(container);

        setTimeout(() => {
            container.classList.add('fade-out');
            fadeOutAudio(1.0);
            setTimeout(() => {
                cleanupAudio()
                container.remove();
                style.remove();
            }, 1000);

        }, REMOVE_DELAY);
    }

    fetch(window.location.href, { method: 'HEAD' })
        .then(response => {
            if (response.status >= 400 && response.status < 600) {
                showImageAndPlaySound();
            }
        })
        .catch(err => {
            console.log(err);
            showImageAndPlaySound();
        });

})();