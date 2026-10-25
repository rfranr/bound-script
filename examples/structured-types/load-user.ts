import type { User } from './types.js';

export async function loadUser(id: string): Promise<User> {
  return { id, name: 'World', active: true, score: 7 };
}
