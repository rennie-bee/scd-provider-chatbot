import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';



const firebaseConfig = {
  apiKey: "AIzaSyDMdsOdPr2dzUT8-34g1xElSi2lrzOKLi0",
  authDomain: "scd-chatbot.firebaseapp.com",
  databaseURL: "https://scd-chatbot-default-rtdb.firebaseio.com",
  projectId: "scd-chatbot",
  storageBucket: "scd-chatbot.appspot.com",
  messagingSenderId: "963935715708",
  appId: "1:963935715708:ios:835819d01bbc11b1a8a4f9",
};

export const FIREBASE_APP = initializeApp(firebaseConfig);
export const FIREBASE_AUTH = getAuth(FIREBASE_APP);
export const FIRESTORE_DB = getFirestore(FIREBASE_APP);