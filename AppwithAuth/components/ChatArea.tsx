import React, { useState } from 'react';
import { ScrollView, StyleSheet, Text, View, Alert, Clipboard, TouchableWithoutFeedback, KeyboardAvoidingView } from 'react-native';

interface Message {
  id: string;
  text: string;
  type: 'sent' | 'received';
  timestamp: string;
}

interface ChatAreaProps {
  messages: Message[];
}

const ChatArea: React.FC<ChatAreaProps> = ({ messages }) => {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const handleLongPress = (text: string, id: string) => {
    Alert.alert(
      'Select Operation',
      'Choose what you want to do with this text:',
      [
        {
          text: 'Copy', onPress: () => {
            Clipboard.setString(text);
            Alert.alert("Copied to clipboard!");
            setSelectedId(null);  // Optionally deselect after action
          }
        },
        {
          text: 'Select Text', onPress: () => {
            setSelectedId(id);
            Alert.alert("Message Selected!");
          }
        },
        { text: 'Cancel', onPress: () => setSelectedId(null), style: 'cancel' },
      ],
      { cancelable: true }
    );
  };
  console.log('ChatArea');
  console.log(messages);
  return (
    <KeyboardAvoidingView style={styles.container} behavior="padding" enabled>
      <ScrollView style={styles.chatContainer}>
        {messages.map((message) => (
          <TouchableWithoutFeedback key={message.id} onLongPress={() => handleLongPress(message.text, message.id)}>
            <View
              style={{
                alignItems: message.type === 'sent' ? 'flex-end' : 'flex-start',
              }}
            >
              <Text style={styles.timestamp}>{message.timestamp}</Text>
              <View
                style={[
                  styles.message,
                  message.type === 'sent' ? styles.sentMessage : styles.receivedMessage,
                  message.id === selectedId ? styles.selectedText : null, // Apply selected style if id matches
                ]}
              >
                <Text
                  style={{
                    color: message.type === 'sent' ? '#ffffff' : '#000000',
                  }}
                >
                  {message.text}
                </Text>
              </View>
            </View>
          </TouchableWithoutFeedback>
        ))}
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
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
    backgroundColor: '#199988',
  },
  receivedMessage: {
    backgroundColor: '#e9edee',
  },
  selectedText: {
    backgroundColor: '#f0e68c', // Highlight color when text is "selected"
  },
  timestamp: {
    color: '#979a9b',
  },
});

export default ChatArea;
