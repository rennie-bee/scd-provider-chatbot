// screens/Profile.js
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { getAuth, signOut } from '@firebase/auth';

const Profile = () => {
  const navigation = useNavigation();
  const auth = getAuth();

  const handleSignOut = async () => {
    try {
      await signOut(auth);
      navigation.navigate('Login');
    } catch (error) {
      console.error('Sign Out Error', error);
    }
  };

  return (
    <View style={styles.container}>
      <Image style={styles.avatar} source={require('./LOGO.png')} />
      <Text style={styles.email}>{auth.currentUser?.email}</Text>
      <TouchableOpacity style={styles.button} onPress={handleSignOut}>
        <Text style={styles.buttonText}>Sign Out</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#e9edee', // Adjusted to match your color scheme
  },
  avatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#D4E7C5', // Temporary placeholder color
    marginBottom: 20,
  },
  email: {
    fontSize: 16,
    color: '#607274', // Text color
    marginBottom: 20,
  },
  button: {
    width: '90%', // Makes the button take up nearly the full width of the screen
    paddingHorizontal: 20,
    paddingVertical: 10,
    backgroundColor: '#199988', // Button color
    borderRadius: 10, // Reduces the radius to make corners less rounded
    justifyContent: 'center', // Center the button text horizontally
    alignItems: 'center', // Center the button text vertically
    marginTop: 20, // Adds space between the email and the button
  },
  buttonText: {
    color: 'white',
    fontSize: 16, // Adjust the font size as needed
  },
});

export default Profile;
