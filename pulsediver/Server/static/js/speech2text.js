// speechRecognition.js

var recognition = new webkitSpeechRecognition();
var recognizing = false;

function startSpeechRecognition() {
    recognition.lang = "zh-CN";
    recognition.continuous = true;
    recognition.interimResults = true;

    var txt = "";
    var test = "";
    var finalTranscript = "";
    var start = Date.now();
    var pauseTime = 15000;

    recognition.onresult = function (event) {
        var result = "";
        for (var i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                result += event.results[i][0].transcript;
                test += result;
            } else {
                result += event.results[i][0].transcript;
            }
        }
        var now = Date.now();
        if (now - start >= pauseTime) {
            finalTranscript += test;
            test = "";
        }
        start = Date.now();
        txt = result;
        document.querySelector('.search-box').value = test; // 将识别结果放入搜索框
    };

    if (!recognizing) {
        recognition.start();
        recognizing = true;
        document.getElementById('micIcon').style.color = 'red'; // 麦克风图标变红
        document.getElementById('micIcon').onmouseover = function() {
            micIcon.title = '语音识别进行中...\n再次点击可结束识别！';

        };
    } else {
        recognition.stop();
        recognizing = false;
        document.getElementById('micIcon').style.color = '#aaa'; // 麦克风图标恢复原色
        document.getElementById('micIcon').onmouseover = function() {
            micIcon.style.color = 'black'
            micIcon.title = '点击开始语音识别... \n(必须为[Edge]或[Chrome]浏览器才可使用此功能)';
        };
         document.getElementById('micIcon').onmouseout = function() {
            micIcon.style.color = '#aaa'
        };
    }

}

