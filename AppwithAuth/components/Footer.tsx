// components/Footer.tsx
import { Ionicons } from '@expo/vector-icons';
import React, { useState } from 'react';
import {
  KeyboardAvoidingView,
  Modal,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  TouchableWithoutFeedback,
  View,
} from 'react-native';

interface Question {
  question: string;
  answer: string;
}

interface FooterProps {
  onSendMessage: (message: string, isQuestion?: boolean) => void;
  qna: Question[];
}

const Footer: React.FC<FooterProps> = ({ onSendMessage, qna }) => {
  const [message, setMessage] = useState('');
  const [showModal, setShowModal] = useState(false);

  const handleSendMessage = () => {
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };

  // return (
  //   <KeyboardAvoidingView
  //     behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
  //     style={styles.container}>
  //     <View style={styles.footer}>
  //       <TextInput
  //         style={styles.input}
  //         value={message}
  //         onChangeText={setMessage}
  //         placeholder="Type a message..."
  //         onSubmitEditing={handleSendMessage}
  //       />
  //       <TouchableOpacity onPress={handleSendMessage}>
  //         <Ionicons name="send" size={24} color="#607274" />
  //       </TouchableOpacity>
  //     </View>
  //   </KeyboardAvoidingView>
  // );
  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={{ width: '100%' }}>
      <View style={styles.container}>
        <TouchableOpacity onPress={() => setShowModal(true)}>
          <Ionicons name="help-circle" size={24} color="#607274" />
        </TouchableOpacity>
        <TextInput
          style={styles.input}
          value={message}
          onChangeText={setMessage}
          placeholder="Type a message..."
        />
        <TouchableOpacity onPress={() => onSendMessage(message)}>
          <Ionicons name="send" size={24} color="#607274" />
        </TouchableOpacity>

        <Modal
          visible={showModal}
          animationType="slide"
          transparent
          onRequestClose={() => setShowModal(false)}>
          <TouchableWithoutFeedback onPress={() => setShowModal(false)}>
            <View style={styles.modalOverlay}>
              <View style={styles.modalView}>
                {qna.map((item, index) => (
                  <TouchableOpacity
                    key={index}
                    onPress={() => {
                      onSendMessage(item.question, true);
                      setShowModal(false);
                    }}>
                    <Text style={styles.questionText}>{item.question}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          </TouchableWithoutFeedback>
        </Modal>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)', // Semi-transparent background
  },
  modalView: {
    margin: 20,
    backgroundColor: 'white',
    borderRadius: 20,
    padding: 35,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
    backgroundColor: '#dce1e1', // Secondary color for the footer background
  },
  input: {
    flex: 1,
    height: 40,
    backgroundColor: '#bcc3c3', // Accent color for the input background
    borderColor: '#9faaab', // Accent color for input border
    borderWidth: 1,
    borderRadius: 20,
    paddingHorizontal: 10,
    marginHorizontal: 8,
    color: '#607274', // Primary color for the input text
  },
  questionText: {
    fontSize: 16,
    color: '#607274', // Primary color for question text
    padding: 10,
  },
});

export default Footer;