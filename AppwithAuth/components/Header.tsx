// components/Header.tsx
import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import { Alert, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useNavigation } from '@react-navigation/native';

const Header: React.FC = () => {
  const navigation = useNavigation();

  const handleAuthAction = () => {
    Alert.alert('Authentication', 'Do you want to logout?',
    [
      {
        text: "Cancel",
        onPress: () => console.log("Cancel Pressed"),
        style: "cancel"
      },
      { text: "Yes",
        onPress: () => {
          console.log("Logout Pressed");
          navigation.navigate('Login' as never);
        }, 
      }
    ]);
  };

  return (
    <View style={styles.header}>
      <Text style={styles.headerText}>Sickle Cell Disease Chat Assistant</Text>
      <TouchableOpacity onPress={handleAuthAction}>
        <Ionicons name="person-circle" size={24} color="black" />
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  header: {
    height: 60,
    width: '100%',
    backgroundColor: '#DED0B6', // Accent Color 1
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#B2A59B', // Accent Color 2
  },
  headerText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#607274', // Primary Color
  },
});

export default Header;