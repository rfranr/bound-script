/** Host-side types mirror the BoundScript interfaces; runtime checks remain authoritative. */
export interface User {
  id: string;
  name: string;
  active: boolean;
  score: number;
}

export interface Greeting {
  message: string;
  recipientId: string;
}
