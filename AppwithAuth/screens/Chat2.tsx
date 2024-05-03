import React, { useState, useEffect } from 'react';
import {
  Keyboard,
  SafeAreaView,
  StatusBar,
  StyleSheet,
  TouchableWithoutFeedback,
} from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import ChatArea from '../components/ChatArea';
import Footer from '../components/Footer';
import Header from '../components/Header';
import {v4 as uuidv4 } from 'uuid';
import { Message } from '../components/types';

// Assuming qna is defined as shown previously

export default function Chat2() {
  const navigation = useNavigation();
  const route = useRoute();
  const { userId } = route.params; // Retrieve userId passed from Login page
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    // Start session and retrieve session ID at the very beginning
    const startSession = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8080/chat/${userId}/start_session`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });

        if (response.ok) {
          const data = await response.json();
          setSessionId(data.session_id);
        } else {
          console.error('Failed to start session:', response.status);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    // console.log(userId);
    startSession();
  }, [userId]);

  // Added fetch request to Flask backend
  const handleSendMessage = async (newMessage: string) => {
    // console.log(sessionId);

    const sentMessage: Message = {
      id: Date.now(),
      message_id: uuidv4(),
      text: newMessage,
      type: 'sent',
      timestamp: `${new Date().getHours()}:${new Date().getMinutes()}, ${new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`,
    };

    setMessages(currentMessages => [...currentMessages, sentMessage]);

    try {
      // Update the URL accordingly
      const response = await fetch(`http://127.0.0.1:8080/chat/${userId}/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message_id: sentMessage.message_id, 
          user_input: sentMessage.text,
          user_input_timestamp: sentMessage.timestamp
        })
      });

      if (response.ok) {
        const data = await response.json();
        const receivedMessage: Message = {
          id: Date.now() + 1,
          message_id: data.message_id,
          text: data.response,
          type: 'received',
          timestamp: `${new Date().getHours()}:${new Date().getMinutes()}, ${new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`,
        };

        setMessages(currentMessages => [...currentMessages, receivedMessage]);
        // Update chatbot response timestamp
        const updateResponse = await fetch(`http://127.0.0.1:8080/chat/${userId}/${sessionId}/${receivedMessage.message_id}/timestamp`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            timestamp: receivedMessage.timestamp
          })
        });

        if(updateResponse.ok) {
          console.log('Update timestamp successfully', response.status);
        }
        else {
          console.error('Failed to update message timestamp', response.status);
        }
      } else {
        console.error('Failed to send message:', response.status);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
        <>
          <StatusBar barStyle="default" />
          <Header />
          <ChatArea messages={messages} />
          <Footer onSendMessage={handleSendMessage} qna={qna} />
        </>
      </TouchableWithoutFeedback>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#dfe4e4', // Adjusted based on your color scheme
  },
});

const qna = [
  {
    question: 'What is Sickle Cell Disease?',
    answer:
      'Sickle cell disease (SCD) and its variants are genetic disorders resulting from the presence of a mutated form of hemoglobin, hemoglobin S (HbS). The most common form of SCD found in North America is homozygous HbS disease (HbSS), an autosomal recessive disorder first described by Herrick in 1910. SCD causes significant morbidity and mortality, particularly in people of African and Mediterranean ancestry. Morbidity, frequency of crisis, degree of anemia, and the organ systems involved vary considerably from individual to individual.',
  },
  // q2
  {
    question: 'Signs and Symptoms of SCD?',
    answer:
      'Sickle cell disease (SCD) presents with a variety of clinical manifestations. Acute and chronic pain, particularly vaso-occlusive crises, are hallmark features. Bone pain, often in the long bones of extremities, stems from bone marrow infarction. Anemia, which is chronic and hemolytic, is a universal presence in SCD. Aplastic crisis, a serious complication, results from parvovirus B19 infection. Splenic sequestration leads to life-threatening anemia with rapid spleen enlargement and high reticulocyte count. Infections, notably encapsulated respiratory bacteria like Streptococcus pneumoniae, pose significant risks, especially in adults with gram-negative organisms such as Salmonella. Growth retardation, delayed sexual maturation, and being underweight are common. Hand-foot syndrome, marked by bilateral painful and swollen hands and/or feet, is prevalent in children. Acute chest syndrome manifests with chest pain, fever, cough, and pulmonary infiltrates, while adults experience dyspnea and severe chest pain. Pulmonary hypertension is increasingly recognized as a serious complication. Avascular necrosis of the femoral or humeral head occurs due to vascular occlusion. Central nervous system involvement includes strokes, while ophthalmologic involvement presents with ptosis, retinal vascular changes, and proliferative retinitis. Cardiac involvement features dilation of ventricles and the left atrium. Gastrointestinal involvement includes cholelithiasis in children and potential liver complications. Genitourinary involvement leads to kidney issues and priapism. Dermatologic involvement manifests as chronic leg ulcers, adding to the complexity of SCD management.',
  },
  // q3
  {
    question: 'What is the diagnosis for SCD?',
    answer:
      'In the United States, mandatory screening for HbS at birth is standard procedure. Prenatal testing is possible through chorionic villus sampling. Diagnostic tests for sickle cell disease (SCD) include hemoglobin electrophoresis, which identifies abnormal hemoglobin variants. A complete blood count (CBC) with differential and reticulocyte count helps assess red blood cell production and turnover. Serum electrolytes are monitored for imbalances, while hemoglobin solubility testing aids in diagnosing sickle cell crises. Peripheral blood smears provide microscopic examination for abnormal cells. Pulmonary function tests, including transcutaneous O2 saturation, evaluate respiratory status. Kidney function is assessed through creatinine, blood urea nitrogen (BUN), and urinalysis. Hepatobiliary function tests, such as ALT and fractionated bilirubin, monitor liver health. Cerebrospinal fluid (CSF) examination, including lumbar puncture (LP), may be necessary in febrile children with toxic appearance or neurological symptoms; CT scanning may precede LP. Blood cultures help identify infectious agents. Arterial blood gases (ABGs) assess respiratory and metabolic status. Secretory phospholipase A2 (sPLA2) levels may be measured to evaluate inflammation and tissue injury in SCD patients. These screening and diagnostic measures are crucial for managing sickle cell disease and its complications effectively.',
  },
  // q4
  {
    question: 'Pharmacotherapy treatments',
    answer:
      'Antimetabolites: Hydroxyurea; Hemoglobin oxygen-affinity modulators (eg, voxelotor); P-selectin inhibitors (eg, crizanlizumab); Gene-editing biologics (ie, exagamglogene autotemcel, lovotibeglogene autotemcel); Opioid analgesics (eg, oxycodone/aspirin, methadone, morphine sulfate, oxycodone/acetaminophen, fentanyl, nalbuphine, codeine, acetaminophen/codeine); Nonsteroidal analgesics (eg, ketorolac, aspirin, acetaminophen, ibuprofen); Tricyclic antidepressants (eg, amitriptyline); Antibiotics (eg, cefuroxime, amoxicillin/clavulanate, penicillin VK, ceftriaxone, azithromycin, cefaclor); Vaccines (eg, pneumococcal, meningococcal, influenza, and recommended scheduled childhood/adult vaccinations); Endothelin-1 receptor antagonists (eg, bosentan); Phosphodiesterase inhibitors (eg, sildenafil, tadalafil); Vitamins (eg, folic acid); L-glutamine; Antiemetics (eg, promethazine).',
  },
  // q5
  {
    question: 'Non-Pharmacotherapy treatments',
    answer:
      'Stem cell transplantation: Can be curative; Transfusions: For sudden, severe anemia due to acute splenic sequestration, parvovirus B19 infection, or hyperhemolytic crises; Wound debridement; Physical therapy; Heat and cold application; Acupuncture and acupressure; Transcutaneous electric nerve stimulation (TENS).',
  },
  // q6
  {
    question:
      'Combination of Pharmacotherapy treatments and Non-Pharmacotherapy treatments',
    answer:
      'Vigorous hydration (plus analgesics): For vaso-occlusive crisis; Oxygen, antibiotics, analgesics, incentive spirometry, simple transfusion, and bronchodilators: For treatment of acute chest syndrome',
  },
  // q7
  {
    question:
      'What is the benefit of the sickle cell trait (SCT) in malaria-endemic areas?',
    answer:
      'Carriers of the sickle cell trait (ie, heterozygotes who carry one HbS allele and one normal adult hemoglobin [HbA] allele) have some resistance to the often-fatal malaria caused by Plasmodium falciparum. This property explains the distribution and persistence of this gene in the population in malaria-endemic areas. However, in areas such as the United States, where malaria is not a problem, the trait no longer provides a survival advantage. Instead, it poses the threat of SCD, which occurs in children of carriers who inherit the sickle cell gene from both parents (ie, HbSS). Although carriers of sickle cell trait do not suffer from SCD, individuals with one copy of HbS and one copy of a gene that codes for another abnormal variant of hemoglobin, such as HbC or Hb beta-thalassemia, have a less severe form of the disease.',
  },
];
