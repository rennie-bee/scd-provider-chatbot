import * as firebase from 'firebase';
import '@firebase/auth';
import '@firebase/firestore';

const firebaseConfig = {
  apiKey: 'AIzaSyBUs7pA3UVTbBrwfWqnrUVNwSlYRZb2DPc',
  authDomain: 'scd-chatbot.firebaseapp.com',
  databaseURL: 'https://scd-chatbot-default-rtdb.firebaseio.com',
  projectId: 'scd-chatbot',
  storageBucket: 'scd-chatbot.appspot.com',
  messagingSenderId: '963935715708',
  appId: '1:963935715708:ios:835819d01bbc11b1a8a4f9',
};

if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}

export { firebase };