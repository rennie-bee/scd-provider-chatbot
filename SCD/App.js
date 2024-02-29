import React, { useState } from 'react';
import { StatusBar, StyleSheet, Text, View, SafeAreaView, TouchableOpacity, Alert, TextInput, TouchableWithoutFeedback, Keyboard, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons'; // Ensure @expo/vector-icons is installed

export default function App() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]); // Array to hold messages

  // Function to handle login/logout action
  const handleAuthAction = () => {
    Alert.alert(
      "Authentication",
      "Do you want to login/logout?",
      [
        {
          text: "Cancel",
          onPress: () => console.log("Cancel Pressed"),
          style: "cancel"
        },
        { text: "Yes", onPress: () => console.log("Login/Logout Pressed") }
      ]
    );
  };

  // Function to handle sending a message
  const handleSendMessage = () => {
    if (message.trim()) {
      // trim the spaces in users' input message
      const requestData = {
        user_input: message.trim(),
      };

      // Use React Native's built-in "fetch" feature to send the POST request
      fetch('http://localhost:8080/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      })
      .then(response => response.json())
      .then(data => {
        console.log('Success:', data);
        if (data && data.response) {
          // Add user input and response  from the chatbot into the array, and display them in the console
          setMessages([...messages, message, "Bot: " + data.response]);
        }
      })
      .catch((error) => {
        console.error('Error:', error);
      });

      // Clear the message input after sending
      setMessage(''); 
    }
  };


  return (
    <SafeAreaView style={styles.container}>
      <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
        <View style={styles.innerContainer}>
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.headerText}>Sickle Cell Disease Chat Assistant</Text>
            <TouchableOpacity style={styles.authIcon} onPress={handleAuthAction}>
              <Ionicons name="person-circle" size={24} color="black" />
            </TouchableOpacity>
          </View>

          {/* Chat Content */}
          <ScrollView style={styles.chatContainer}>
            {messages.map((msg, index) => (
              <View key={index} style={styles.message}>
                <Text>{msg}</Text>
              </View>
            ))}
          </ScrollView>

          {/* KeyboardAvoidingView wraps the footer to move it above the keyboard */}
          <KeyboardAvoidingView
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            keyboardVerticalOffset={Platform.OS === "ios" ? 60 : 20}>
            <View style={styles.footer}>
              <TextInput
                style={styles.input}
                value={message}
                onChangeText={setMessage}
                placeholder="Type a message..."
                onSubmitEditing={handleSendMessage}
              />
              <TouchableOpacity onPress={handleSendMessage}>
                <Ionicons name="send" size={24} color="blue" />
              </TouchableOpacity>
            </View>
          </KeyboardAvoidingView>
        </View>
      </TouchableWithoutFeedback>
      <StatusBar style="auto" />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f0f0', // Gray background
  },
  innerContainer: {
    flex: 1,
  },
  header: {
    height: 60,
    width: '100%',
    backgroundColor: '#fff', // White color for header
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
  chatContainer: {
    flex: 1,
    padding: 10,
  },
  message: {
    backgroundColor: '#e0e0e0',
    padding: 10,
    borderRadius: 10,
    marginVertical: 5,
  },
  footer: {
    flexDirection: 'row',
    height: 60,
    paddingHorizontal: 10,
    backgroundColor: '#fff',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  input: {
    flex: 1,
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    borderRadius: 20,
    paddingHorizontal: 10,
    marginRight: 10,
  },
});
