var mainApp = {};

(function(){
var firbase = app_firbase;
var user_id = null;

firebase.auth().onAuthStateChanged(function(user) {
    if (user) {
      // User is signed in.
      user_id = user.user_id;
    }
    else{
        user_id = null;
        window.location.replace("login.html")
    }
  });
  function logOut(){
      firebase.auth().signOut();
  }

  mainApp.logOut = logOut;
})()