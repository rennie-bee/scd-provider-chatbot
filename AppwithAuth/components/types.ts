// types.ts
export interface Message {
    id: number;
    text: string;
    type: 'sent' | 'received';
    timestamp: string;
  }
  