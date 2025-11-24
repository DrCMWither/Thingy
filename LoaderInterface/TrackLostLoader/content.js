(function() {
    const REMOVE_DELAY = 50000;
    const STRIPE_OFFSET_PX = 140;
    const AUDIO_TRACK_LOST = chrome.runtime.getURL("track_fail.wav");
    const AUDIO_FAIL_FULL = chrome.runtime.getURL("res_fail_full.ogg");
    const AUDIO_FAIL_LOOP = chrome.runtime.getURL("res_fail_loop.ogg");

    const IMG_END_MID_F = chrome.runtime.getURL("end_mid_f.png");
    const IMG_CLEAR_FAIL = chrome.runtime.getURL("clear_fail.png");
    const IMG_STRIPE_TOP = chrome.runtime.getURL("stripe_top.png");
    const IMG_STRIPE_BOTTOM = chrome.runtime.getURL("stripe_bottom.png");
    const IMG_PAUSE_BG = chrome.runtime.getURL("pausebg.png");

    let currentAudio = null;

    function playSoundSequence() {
        const audio1 = new Audio(AUDIO_TRACK_LOST);
        audio1.volume = 0.6;
        currentAudio = audio1;

        audio1.addEventListener('ended', () => {
            if (!document.getElementById('tracklost-container')) return;

            const audio2 = new Audio(AUDIO_FAIL_FULL);
            audio2.volume = 0.6;
            currentAudio = audio2;

            audio2.addEventListener('ended', () => {
                if (!document.getElementById('tracklost-container')) return;

                const audio3 = new Audio(AUDIO_FAIL_LOOP);
                audio3.volume = 0.6;
                audio3.loop = true;
                currentAudio = audio3;

                audio3.play().catch(e => console.log("Loop Audio blocked:", e));
            });

            audio2.play().catch(e => console.log("Full Audio blocked:", e));
        });

        audio1.play().catch(error => {
            console.log("Initial Audio blocked by browser policy:", error);
        });
    }

    function stopCurrentAudio() {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
            currentAudio = null;
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

        const group3 = document.createElement('div');
        group3.className = 'tl-group-3';
        group3.innerHTML = `<img src="${IMG_PAUSE_BG}" alt="Background">`;

        const group2 = document.createElement('div');
        group2.className = 'tl-group-2';
        group2.innerHTML = `
            <img src="${IMG_STRIPE_TOP}" class="tl-stripe tl-stripe-top" alt="Stripe Top">
            <img src="${IMG_STRIPE_BOTTOM}" class="tl-stripe tl-stripe-bottom" alt="Stripe Bottom">
        `;

        const group1 = document.createElement('div');
        group1.className = 'tl-group-1';
        group1.innerHTML = `
            <img src="${IMG_END_MID_F}" class="tl-img-end-mid" alt="End Mid">
            <img src="${IMG_CLEAR_FAIL}" class="tl-img-clear-fail" alt="Fail Text">
        `;

        container.appendChild(group3);
        container.appendChild(group2);
        container.appendChild(group1);

        document.body.appendChild(container);

        setTimeout(() => {
            container.classList.add('fade-out');

            setTimeout(() => {
                stopCurrentAudio();
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