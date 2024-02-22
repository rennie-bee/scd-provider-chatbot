// components/ChatArea.tsx
import React from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';

interface ChatAreaProps {
  messages: string[];
}

const ChatArea: React.FC<ChatAreaProps> = ({ messages }) => {
  return (
    <ScrollView style={styles.chatContainer}>
      {messages.map((msg, index) => (
        <View key={index} style={styles.message}>
          <Text>{msg}</Text>
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
    backgroundColor: '#e0e0e0',
    padding: 10,
    borderRadius: 10,
    marginVertical: 5,
  },
});

export default ChatArea;
