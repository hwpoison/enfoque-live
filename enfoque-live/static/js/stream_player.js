var player = videojs('stream');
player.fluid(true)

function refreshVideoContent(){
    player.src({
      type: 'application/vnd.apple.mpegurl',
      src: '/monitoring/stream.m3u8'
    });
    player.play()
}

player.on('error', () => {
    let Interval;
    player.error('Actualmente no hay una transmisión en curso. Cuando esta comience se comenzará a reproducir automaticamente.')
    Interval = setInterval(()=>{fetch('/status')
      .then(response => {
        if (response.ok) {
            refreshVideoContent()
            clearInterval(Interval)
        }
      })
      .catch(error => {
        console.error('Error trying to connect to the server:', error);
      })}, 10000);
})