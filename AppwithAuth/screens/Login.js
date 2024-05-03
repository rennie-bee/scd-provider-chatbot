import React, { useState, useEffect } from 'react';
import { View, Text, Alert, TextInput, Button, StyleSheet, ScrollView } from 'react-native';
import { initializeApp } from '@firebase/app';
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, onAuthStateChanged, signOut } from '@firebase/auth';
import { useNavigation } from '@react-navigation/native';


const firebaseConfig = {
  apiKey: "AIzaSyDMdsOdPr2dzUT8-34g1xElSi2lrzOKLi0",
  authDomain: "scd-chatbot.firebaseapp.com",
  databaseURL: "https://scd-chatbot-default-rtdb.firebaseio.com",
  projectId: "scd-chatbot",
  storageBucket: "scd-chatbot.appspot.com",
  messagingSenderId: "963935715708",
  appId: "1:963935715708:web:1acb02b923b5c262a8a4f9",
  measurementId: "G-MFNWKJJNST"
};

const app = initializeApp(firebaseConfig);

const AuthScreen = ({ email, setEmail, password, setPassword, isLogin, setIsLogin, handleAuthentication }) => {
  return (
    <View style={styles.authContainer}>
       <Text style={styles.title}>{isLogin ? 'Sign In' : 'Sign Up'}</Text>

       <TextInput
        style={styles.input}
        value={email}
        onChangeText={setEmail}
        placeholder="Email"
        autoCapitalize="none"
      />
      <TextInput
        style={styles.input}
        value={password}
        onChangeText={setPassword}
        placeholder="Password"
        secureTextEntry
      />
      <View style={styles.buttonContainer}>
        <Button title={isLogin ? 'Sign In' : 'Sign Up'} onPress={handleAuthentication} color="#3498db" />
      </View>

      <View style={styles.bottomContainer}>
        <Text style={styles.toggleText} onPress={() => setIsLogin(!isLogin)}>
          {isLogin ? 'Need an account? Sign Up' : 'Already have an account? Sign In'}
        </Text>
      </View>
    </View>
  );
}


// const AuthenticatedScreen = ({ user, handleAuthentication }) => {
//     const navigation = useNavigation()
//     const gotoChat = () => {
//         navigation.navigate('Chat')
//     }
//   return (
//     <View style={styles.authContainer}>
//       <Button title="Logout" onPress={handleAuthentication} color="#e74c3c" />
//     </View>
//   );
// };

export default Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [user, setUser] = useState(null); // Track user authentication state
  const [isLogin, setIsLogin] = useState(true);

  const auth = getAuth(app);
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
    });

    return () => unsubscribe();
  }, [auth]);

  const navigation = useNavigation()
  const gotoChat = (id) => {
      navigation.navigate('Chat', { userId: id })
  }
  
  const handleAuthentication = async () => {
    try {
      let uid; // Retrieve uid
      if (isLogin) {
        // Sign in
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        console.log('User signed in successfully!');
        uid = userCredential.user.uid;
      } else {
        // Sign up
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        console.log('User created successfully!');
        uid = userCredential.user.uid;
      }
      gotoChat(uid); // Pass uid to chat page
    } catch (error) {
      Alert.alert('Authentication error:', error.message);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      {!user ? (
        // Show user's email if user is authenticated
        // <AuthenticatedScreen user={user} handleAuthentication={handleAuthentication} />
        <AuthScreen
          email={email}
          setEmail={setEmail}
          password={password}
          setPassword={setPassword}
          isLogin={isLogin}
          setIsLogin={setIsLogin}
          handleAuthentication={handleAuthentication}
        />
      ) : (
        // Show sign-in or sign-up form if user is not authenticated
        <AuthScreen
          email={email}
          setEmail={setEmail}
          password={password}
          setPassword={setPassword}
          isLogin={isLogin}
          setIsLogin={setIsLogin}
          handleAuthentication={handleAuthentication}
        />
      )}
    </ScrollView>
  );
}
const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#f0f0f0',
  },
  authContainer: {
    width: '80%',
    maxWidth: 400,
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    elevation: 3,
  },
  title: {
    fontSize: 24,
    marginBottom: 16,
    textAlign: 'center',
  },
  input: {
    height: 40,
    borderColor: '#ddd',
    borderWidth: 1,
    marginBottom: 16,
    padding: 8,
    borderRadius: 4,
  },
  buttonContainer: {
    marginBottom: 16,
  },
  toggleText: {
    color: '#3498db',
    textAlign: 'center',
  },
  bottomContainer: {
    marginTop: 20,
  },
  emailText: {
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 20,
  },
});
