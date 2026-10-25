import type { Greeting, User } from './types.js';

export function greet(user: User): Greeting {
  return { message: `Hello, ${user.name}!`, recipientId: user.id };
}
