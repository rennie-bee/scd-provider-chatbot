// types.ts
export interface Message {
    id: number;
    message_id: string;
    text: string;
    type: 'sent' | 'received';
    timestamp: string;
  }
  