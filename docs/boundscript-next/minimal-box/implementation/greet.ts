import type { GreetingBox } from '../inputs/contract.ts';

export const greet: GreetingBox = (name, slugger) => {
  const trimmedName = name.trim();
  const slug = slugger(trimmedName);
  return `Hello, ${trimmedName}! [${slug}]`;
};
