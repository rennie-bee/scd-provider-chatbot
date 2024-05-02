import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, ScrollView, Modal, TextInput } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { getAuth, signOut } from '@firebase/auth';

const Profile = () => {
  const navigation = useNavigation();
  const auth = getAuth();
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [username, setUsername] = useState(''); // Placeholder for username state

  const handleSignOut = async () => {
    try {
      await signOut(auth);
      navigation.navigate('Login');
    } catch (error) {
      console.error('Sign Out Error', error);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.headerContainer}>
        <Image
          style={styles.coverPhoto}
          source={{uri: 'https://assets.bwbx.io/images/users/iqjWHBFdfxIU/iRRvgn3rECGM/v1/1200x800.jpg'}}
        />
        <View style={styles.profileContainer}>
          <Image
            style={styles.profilePhoto}
            source={{uri: 'https://st2.depositphotos.com/4060975/9157/v/450/depositphotos_91577612-stock-illustration-doctor-colored-vector-icon.jpg'}}
          />
          <Text style={styles.nameText}>Username</Text>
        </View>
      </View>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>
        <View style={styles.infoContainer}>
          <Text style={styles.infoText}>Full Name: Username</Text>
          <Text style={styles.infoText}>Email: {auth.currentUser?.email}</Text>
          <Text style={styles.infoText}>Medical ID: 000001</Text>
        </View>
      </View>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>App</Text>
        <View style={styles.infoContainer}>
          <Text style={styles.infoText}>Color Scheme</Text>
          <Text style={styles.infoText}>Haptic Feedback</Text>
        </View>
      </View>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <View style={styles.infoContainer}>
          <Text style={styles.infoText}>Privacy Policy</Text>
          <Text style={styles.infoText}>Version: 0.8</Text>
        </View>
      </View>
      <TouchableOpacity style={styles.editButton} onPress={() => setEditModalVisible(true)}>
        <Text style={styles.buttonText}>Edit Profile</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.button} onPress={handleSignOut}>
        <Text style={styles.buttonText}>Sign Out</Text>
      </TouchableOpacity>
      <Modal
        animationType="slide"
        transparent={true}
        visible={editModalVisible}
        onRequestClose={() => setEditModalVisible(false)}
      >
        <View style={styles.centeredView}>
          <View style={styles.modalView}>
            <TextInput
              style={styles.modalInput}
              onChangeText={setUsername}
              value={username}
              placeholder="Username"
            />
            <TextInput
              style={styles.modalInput}
              onChangeText={(text) => auth.currentUser.updateEmail(text)}
              value={auth.currentUser?.email}
              placeholder="Email"
            />
            <TouchableOpacity
              style={styles.saveButton}
              onPress={() => {
                setEditModalVisible(false);
              }}
            >
              <Text style={styles.saveButtonText}>Save Profile</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  headerContainer: {
    alignItems: 'center',
  },
  coverPhoto: {
    width: '100%',
    height: 200,
  },
  profileContainer: {
    alignItems: 'center',
    marginTop: -50,
  },
  profilePhoto: {
    width: 100,
    height: 100,
    borderRadius: 50,
  },
  nameText: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 10,
  },
  section: {
    // backgroundColor: '#E1F0DA',
    padding: 10,
    marginTop: 5,
    marginLeft: 15,
    marginRight: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  infoContainer: {
    backgroundColor: '#D4E7C5', // Slightly different gray for the list background
    borderRadius: 10,
    padding: 10,
  },
  infoText: {
    fontSize: 16,
    marginBottom: 10,
  },
  editButton: {
    backgroundColor: '#000000', // Black color for edit button
    borderRadius: 5,
    padding: 10,
    marginLeft: 20,
    marginRight: 20,
    marginTop: 20,
    alignItems: 'center',
  },
  button: {
    backgroundColor: '#199988', // Sign out button color
    borderRadius: 5,
    padding: 10,
    margin: 20,
    alignItems: 'center',
  },
  buttonText: {
    fontSize: 16,
    color: '#fff',
    textAlign: 'center',
  },
  centeredView: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 22,
    backgroundColor: 'rgba(0, 0, 0, 0.5)', // Semi-transparent background for modal
  },
  modalView: {
    margin: 20,
    backgroundColor: 'white',
    borderRadius: 20,
    padding: 35,
    alignItems: 'center',
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2
    },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5
  },
  modalInput: {
    width: '90%', // Set width to 90% to match the button
    marginBottom: 15,
    padding: 10,
    borderColor: '#ddd',
    borderWidth: 1,
    borderRadius: 5,
  },
  saveButton: {
    width: '90%', // Ensure the button also has a width of 90%
    backgroundColor: '#199988',
    borderRadius: 5,
    padding: 10,
    marginTop: 10,
    alignItems: 'center', // Center the text inside the button
  },
  saveButtonText: {
    color: 'white',
    fontSize: 16,
    textAlign: 'center',
  },
});

export default Profile;
