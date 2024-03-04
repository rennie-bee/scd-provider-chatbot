import React, { useState } from 'react';
import {
  Keyboard,
  SafeAreaView,
  StatusBar,
  StyleSheet,
  TouchableWithoutFeedback,
} from 'react-native';
import ChatArea from '../components/ChatArea';
import Footer from '../components/Footer';
import Header from '../components/Header';
import { Message } from '../components/types';

// Assuming qna is defined as shown previously

export default function Chat2() {
  const [messages, setMessages] = useState<Message[]>([]);

  const handleSendMessage = (
    newMessage: string,
    isQuestion: boolean = false,
  ) => {
    const now = new Date();
    const timestamp = `${now.getHours()}:${now.getMinutes()}, ${now.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;

    // For both question and manual messages, add the sent message
    const sentMessage: Message = {
      id: Date.now(),
      text: newMessage,
      type: 'sent',
      timestamp,
    };
    setMessages(currentMessages => [...currentMessages, sentMessage]);

    if (isQuestion) {
      // Handle question-specific logic here
      const question = qna.find(q => q.question === newMessage);
      if (question) {
        const answerMessage: Message = {
          id: Date.now() + 1,
          text: question.answer,
          type: 'received',
          timestamp,
        };
        setMessages(currentMessages => [...currentMessages, answerMessage]);
      }
    } else {
      // For manual messages, generate an automated response if desired
      // Example: Echo the message or provide a generic bot response
      const responseMessage: Message = {
        id: Date.now() + 1,
        text: 'Echo: ' + newMessage, // Customize this as needed
        type: 'received',
        timestamp,
      };
      setMessages(currentMessages => [...currentMessages, responseMessage]);
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
    backgroundColor: '#FAEED1', // Adjusted based on your color scheme
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
