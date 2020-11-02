(function(){

    var ui = new firebaseui.auth.AuthUI(firebase.auth());

    var uiConfig = {
        callbacks: {
          signInSuccessWithAuthResult: function(authResult, redirectUrl) {
            // User successfully signed in.
            // Return type determines whether we continue the redirect automatically
            // or whether we leave that to developer to handle.
            return true;
          },


          uiShown: function() {
            // The widget is rendered.
            // Hide the loader.
            document.getElementById('loader').style.display = 'none';
          }
        },


        
        signInFlow: 'popup',
        signInSuccessUrl: 'nettside.html',
        signInOptions: [
          //  Leave the lines as is for the providers you want to offer your users.
          firebase.auth.GoogleAuthProvider.PROVIDER_ID,
          firebase.auth.FacebookAuthProvider.PROVIDER_ID,
         firebase.auth.TwitterAuthProvider.PROVIDER_ID,
          firebase.auth.GithubAuthProvider.PROVIDER_ID,
          firebase.auth.EmailAuthProvider.PROVIDER_ID,
        ],


        // Terms of service url.
        tosUrl: '<your-tos-url>',


        // Privacy policy url.
        privacyPolicyUrl: '<your-privacy-policy-url>'
      };


      // The start method will wait until the DOM is loaded.
ui.start('#firebaseui-auth-container', uiConfig);



})()