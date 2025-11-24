(function() {

    const REMOVE_DELAY = 5000;
    const AUDIO_URL = chrome.runtime.getURL("track_lost.mp3");
    const IMG_URL = chrome.runtime.getURL("Title-tracklost.webp");

    function playSound() {
        const audio = new Audio(AUDIO_URL);
        audio.volume = 0.6;
        const playPromise = audio.play();
        if (playPromise !== undefined) {
            playPromise.catch(error => {
                console.log("Track Lost Sound blocked by browser policy:", error);
            });
        }
    }

    function showImageAndPlaySound() {
        playSound();

        const style = document.createElement('style');
        style.textContent = `
            #tracklost-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                pointer-events: none;
                overflow: hidden;
            }
            #tracklost-container img {
                width: 100%;
                height: 100%;
                object-fit: cover; /* 保持纵横比，裁剪溢出部分 */
            }
            #tracklost-container.fade-out {
                opacity: 0;
                transition: opacity 1s;
            }
        `;
        document.head.appendChild(style);

        const container = document.createElement('div');
        container.id = 'tracklost-container';
        container.innerHTML = `<img src="${IMG_URL}">`;
        document.body.appendChild(container);

        setTimeout(() => {
            container.classList.add('fade-out');
            setTimeout(() => {
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
