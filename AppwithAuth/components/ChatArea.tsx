import React, { useState } from 'react';
import { ScrollView, StyleSheet, Text, View, Alert, Clipboard, TouchableWithoutFeedback } from 'react-native';
import { Message } from '../components/types'; // Ensure this import path matches your project structure

interface ChatAreaProps {
  messages: Message[];
}

const ChatArea: React.FC<ChatAreaProps> = ({ messages }) => {
  const handleLongPress = (text) => {
    Alert.alert(
      'Select Operation',
      'Choose what you want to do with this text:',
      [
        { text: 'Copy', onPress: () => Clipboard.setString(text) },
        { text: 'Select Text', onPress: () => console.log('Select Text') },
        { text: 'Cancel', onPress: () => console.log('Cancelled'), style: 'cancel' },
      ],
      { cancelable: true }
    );
  };

  return (
    <ScrollView style={styles.chatContainer}>
      {messages.map((message) => (
        <TouchableWithoutFeedback key={message.id} onLongPress={() => handleLongPress(message.text)}>
          <View
            style={{
              alignItems: message.type === 'sent' ? 'flex-end' : 'flex-start',
            }}>
            <Text style={styles.timestamp}>{message.timestamp}</Text>
            <View
              style={[
                styles.message,
                message.type === 'sent'
                  ? styles.sentMessage
                  : styles.receivedMessage,
              ]}>
              <Text
                style={{
                  color: message.type === 'sent' ? '#ffffff' : '#000000',
                }}>
                {message.text}
              </Text>
            </View>
          </View>
        </TouchableWithoutFeedback>
      ))}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  chatContainer: {
    flex: 1,
    padding: 10,
  },
  message: {
    padding: 10,
    borderRadius: 10,
    marginVertical: 5,
    maxWidth: '70%',
  },
  sentMessage: {
    backgroundColor: '#199988', // Primary Color for sent messages
  },
  receivedMessage: {
    backgroundColor: '#e9edee', // Accent Color 2 for received messages
  },
  timestamp: {
    color: '#979a9b', // Accent Color 1
  },
});

export default ChatArea;
