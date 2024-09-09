// components/Header.tsx
import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import { Alert, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

const Header: React.FC = () => {
  const handleAuthAction = () => {
    Alert.alert('Authentication', 'Do you want to login/logout?');
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
    backgroundColor: '#fff',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
});

export default Header;
