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
