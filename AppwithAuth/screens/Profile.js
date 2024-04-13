// screens/Profile.js
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { getAuth, signOut } from '@firebase/auth';

// const Profile = () => {
//   const navigation = useNavigation();
//   const auth = getAuth();

//   const handleSignOut = async () => {
//     try {
//       await signOut(auth);
//       navigation.navigate('Login');
//     } catch (error) {
//       console.error('Sign Out Error', error);
//     }
//   };

//   return (
//     <View style={styles.container}>
//       <Image style={styles.avatar} source={require('./LOGO.png')} />
//       <Text style={styles.email}>{auth.currentUser?.email}</Text>
//       <TouchableOpacity style={styles.button} onPress={handleSignOut}>
//         <Text style={styles.buttonText}>Sign Out</Text>
//       </TouchableOpacity>
//     </View>
//   );
// };

// const styles = StyleSheet.create({
//   container: {
//     flex: 1,
//     justifyContent: 'center',
//     alignItems: 'center',
//     backgroundColor: '#e9edee', // Adjusted to match your color scheme
//   },
//   avatar: {
//     width: 100,
//     height: 100,
//     borderRadius: 50,
//     backgroundColor: '#D4E7C5', // Temporary placeholder color
//     marginBottom: 20,
//   },
//   email: {
//     fontSize: 16,
//     color: '#607274', // Text color
//     marginBottom: 20,
//   },
//   button: {
//     width: '90%', // Makes the button take up nearly the full width of the screen
//     paddingHorizontal: 20,
//     paddingVertical: 10,
//     backgroundColor: '#199988', // Button color
//     borderRadius: 10, // Reduces the radius to make corners less rounded
//     justifyContent: 'center', // Center the button text horizontally
//     alignItems: 'center', // Center the button text vertically
//     marginTop: 20, // Adds space between the email and the button
//   },
//   buttonText: {
//     color: 'white',
//     fontSize: 16, // Adjust the font size as needed
//   },
// });

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
      <View style={styles.bioContainer}>
        <Text style={styles.bioText}>
          {auth.currentUser?.email}
        </Text>
      </View>
      <View style={styles.statsContainer}>
        <View style={styles.statContainer}>
          <Text style={styles.statCount}>1234</Text>
          <Text style={styles.statLabel}>Posts</Text>
        </View>
        <View style={styles.statContainer}>
          <Text style={styles.statCount}>5678</Text>
          <Text style={styles.statLabel}>Followers</Text>
        </View>
        <View style={styles.statContainer}>
          <Text style={styles.statCount}>9101</Text>
          <Text style={styles.statLabel}>Following</Text>
        </View>
      </View>
      {/* <TouchableOpacity style={styles.button} onPress={handleEditPress}>
        <Text style={styles.buttonText}>Edit Profile</Text>
      </TouchableOpacity> */}
      <TouchableOpacity style={styles.button} onPress={handleSignOut}>
        <Text style={styles.buttonText}>Sign Out</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = {
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
  bioContainer: {
    padding: 15,
  },
  bioText: {
    fontSize: 16,
  },
  statsContainer: {
    flexDirection: 'row',
    marginTop: 20,
    marginBottom: 20,
  },
  statContainer: {
    alignItems: 'center',
    flex: 1,
  },
  statCount: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  statLabel: {
    fontSize: 16,
    color: '#999',
  },
  button: {
    backgroundColor: '#199988',
    borderRadius: 5,
    padding: 10,
    marginHorizontal: 20,
  },
  buttonText: {
    fontSize: 16,
    color: '#fff',
    textAlign: 'center',
  },
};

export default Profile;
