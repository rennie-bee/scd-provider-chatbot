import * as firebase from 'firebase';
import '@firebase/auth';
import '@firebase/firestore';

const firebaseConfig = {
//   apiKey: 'YOUR_KEY_HERE_AIzaSyAOWH',
//   authDomain: 'your-auth-domain-b1234.firebaseapp.com',
//   databaseURL: 'https://your-database-name.firebaseio.com',
  projectId: 'scd-chatbot',
//   storageBucket: 'your-project-id-1234.appspot.com',
//   messagingSenderId: '12345-insert-yourse',
  appId: '1:963935715708:ios:835819d01bbc11b1a8a4f9',
};

if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}

export { firebase };