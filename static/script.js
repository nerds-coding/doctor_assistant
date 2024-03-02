document.addEventListener('DOMContentLoaded', function () {
    var speakButton = document.getElementById('speakButton');
    var inputDisplay = document.getElementById('inputDisplay');
    var outputDisplay = document.getElementById('outputDisplay');

    speakButton.addEventListener('click', function () {
        inputDisplay.innerText = "Listening...";
        var recognition = new webkitSpeechRecognition();
        recognition.lang = 'en-US';

        recognition.onresult = function (event) {
            var transcript = event.results[0][0].transcript;
            inputDisplay.innerText = "You said: " + transcript;
            sendSpeech(transcript);
        };

        recognition.start();
    });

    function sendSpeech(transcript) {
        fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: transcript })
        })
            .then(response => response.json())
            .then(data => {
                outputDisplay.innerText = "Doctor's Assistant: " + data.response;
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
});
