import type { Greeting } from './types.js';

export function createDisplay(writeLine: (message: string) => void): (greeting: Greeting) => void {
  return (greeting) => { writeLine(greeting.message); };
}
