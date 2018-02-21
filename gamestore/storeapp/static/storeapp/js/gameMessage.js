//gets the value of the cookie given in the parameter
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function csrfSafeMethod(method) {
  //these methods shouldn't need csrf protections
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

//get csrf token from cookie
var csrftoken = getCookie("csrftoken");

//makes sure that an anti-csrf token is added to ajax requests with side effects
$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  }
});



$(document).ready(function() {

  //build a string to match event origin against
  var urlString = $("#game-iframe").attr("src");
  var urlArray = urlString.split("/");
  var base = urlArray[0] + "//" + urlArray[2];

  function loadButtonHandler(clickEvt) {
    $.get({
      contentType: "application/json",
      data: {
        messageType: 'LOAD_CHOSEN',
        saveID: clickEvt.target.name,
        gameID: gameID
      },
      url: "/msg/",
      dataType: "json",
      success: function(resData) {
        $("#msg-feedback").empty();
        var gameFrame = document.getElementById("game-iframe");
        gameFrame.contentWindow.postMessage({
          messageType: 'LOAD',
          gameState: JSON.parse(resData)
        }, base);
      }
    });
  }

  //add listener for messages the game sends
  window.addEventListener("message", function(evt) {
    if (evt.origin === base) {
      evt.data.gameID = gameID;
      switch(evt.data.messageType) {
        case "SCORE":
          $.post({
            contentType: "application/json",
            data: JSON.stringify(evt.data),
            url: "/msg/",
            dataType: "text",
            success: function(resData) {
              $("#msg-feedback").text(resData);
            }
          });
          break;
        case "SAVE":
          evt.data.saveName = prompt("Please enter a name for your save", "mysave");
          if (evt.data.saveName === null) {
            break;
          }
          $.post({
            contentType: "application/json",
            data: JSON.stringify(evt.data),
            url: "/msg/",
            dataType: "text",
            success: function(resData) {
              $("#msg-feedback").text(resData);
            }
          });
          break;
        case "LOAD_REQUEST":
          $.get({
            contentType: "application/json",
            data: evt.data,
            url: "/msg/",
            dataType: "html",
            success: function(resData) {
              $("#msg-feedback").text("");
              $("#msg-feedback").append(resData);
              $(".save-selector").click(loadButtonHandler);
            }
          });
          break;
        case "SETTING":
            $("#game-iframe").attr(evt.data.options)
          break;
        default:
          break;
      }
    }
  });
});
