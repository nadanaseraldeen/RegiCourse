var linkLogin = document.getElementById("linkLogin");
var linkSignup = document.getElementById("linkSignup");
var loginForm = document.getElementById("loginForm");
var signupForm = document.getElementById("signupForm");

function openTab(tabname) {
  if (tabname == "Login") {
    loginForm.classList.add("active-form");
    signupForm.classList.remove("active-form");
    linkLogin.classList.add("active-link");
    linkSignup.classList.remove("active-link");
  } else if (tabname == "Signup") {
    signupForm.classList.add("active-form");
    loginForm.classList.remove("active-form");
    linkLogin.classList.remove("active-link");
    linkSignup.classList.add("active-link");
  }
}
