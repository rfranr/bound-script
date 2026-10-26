import type { GreetingBox } from '../inputs/contract.ts';

export const greet: GreetingBox = (name, slugger) => {
  const trimmed = name.trim();
  return `Hello, ${trimmed}! [${slugger(trimmed)}]`;
};
