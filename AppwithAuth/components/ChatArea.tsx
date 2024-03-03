// components/ChatArea.tsx
import React from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { Message } from '../components/types'; // Ensure this import path matches your project structure

interface ChatAreaProps {
  messages: Message[];
}

const ChatArea: React.FC<ChatAreaProps> = ({ messages }) => {
  return (
    <ScrollView style={styles.chatContainer}>
      {messages.map(message => (
        <View
          key={message.id}
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
    backgroundColor: '#607274', // Primary Color for sent messages
    color: '#FAEED1', // Secondary Color for text
  },
  receivedMessage: {
    backgroundColor: '#B2A59B', // Accent Color 2 for received messages
    color: '#FAEED1', // Secondary Color for text
  },
  // Timestamp and other styles...
  timestamp: {
    color: '#DED0B6', // Accent Color 1
  },
});

export default ChatArea;