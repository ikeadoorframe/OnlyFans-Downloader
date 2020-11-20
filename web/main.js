  function StartDownloading(){
    var username = document.getElementById("username").value;
    var access_token = document.getElementById("access_token").value
    var user_agent = document.getElementById("user_agent").value
    var post_amount = document.getElementById("post_amount").value
    eel.start(username, access_token, user_agent, post_amount)
  }

function sendLog(text){
var log = document.getElementById('ConsoleLog');
  log.value += text;
  log.scrollTop = log.scrollHeight;
}
eel.expose(sendLog);
