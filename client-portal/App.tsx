// App.tsx
import React, { useState } from 'react';
import {
  Keyboard,
  SafeAreaView,
  StatusBar,
  StyleSheet,
  TouchableWithoutFeedback,
} from 'react-native';
import ChatArea from './components/ChatArea';
import Footer from './components/Footer';
import Header from './components/Header';

export default function App() {
  const [messages, setMessages] = useState<string[]>([]);

  const handleSendMessage = (newMessage: string) => {
    setMessages([...messages, newMessage]);
  };

  // For 24 Spring: New "handleSendMessage" function to integrate with the flask server:
  // const handleSendMessage = async (newMessage: string) => {
  //   try {
  //     const payload = {
  //       user_input: newMessage,
  //     };

  //     // Make a POST request to the backend
  //     /* If using an Android emulator and both the emulator and the server are on the same machine:
  //        Change the following address to "http://10.0.2.2:8080/chat" instead. */
  //     const response = await fetch('http://127.0.0.1:8080/chat', {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json',
  //       },
  //       body: JSON.stringify(payload),
  //     });

  //     // Parse the JSON response from the backend
  //     const data = await response.json();

  //     if (response.ok) {
  //       // Update the chat with the response from the backend
  //       setMessages((prevMessages) => [...prevMessages, newMessage, data.response]);
  //     } else {
  //       // Handle any errors or non-OK responses here
  //       console.error('Error from backend:', data.error);
  //     }
  //   } catch (error) {
  //     console.error('Failed to send message:', error);
  //   }
  // };

  return (
    <SafeAreaView style={styles.container}>
      <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
        <>
          <StatusBar barStyle="default" />
          <Header />
          <ChatArea messages={messages} />
          <Footer onSendMessage={handleSendMessage} />
        </>
      </TouchableWithoutFeedback>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f0f0',
  },
});
