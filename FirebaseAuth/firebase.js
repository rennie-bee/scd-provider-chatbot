import * as firebase from "firebase";

const firebaseConfig = {
  apiKey: "AIzaSyDMdsOdPr2dzUT8-34g1xElSi2lrzOKLi0",
  authDomain: "scd-chatbot.firebaseapp.com",
  databaseURL: "https://scd-chatbot-default-rtdb.firebaseio.com",
  projectId: "scd-chatbot",
  storageBucket: "scd-chatbot.appspot.com",
  messagingSenderId: "963935715708",
  appId: "1:963935715708:web:1acb02b923b5c262a8a4f9",
};

// Initialize Firebase
let app;
if (firebase.apps.length === 0) {
  app = firebase.initializeApp(firebaseConfig);
} else {
  app = firebase.app()
}

const auth = firebase.auth()

export { auth };