import type { Slugger } from './slugger.ts';

export type GreetingBox = (name: string, slugger: Slugger) => string;
