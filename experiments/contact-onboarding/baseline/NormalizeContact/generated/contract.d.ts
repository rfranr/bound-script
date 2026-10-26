export interface ContactSubmission {
    requestId: string;
    name: string;
    email: string;
    locale: string;
    consent: boolean;
    trialDays: number;
}
export interface NormalizedContact {
    requestId: string;
    displayName: string;
    email: string;
    locale: string;
    consent: boolean;
    trialDays: number;
    valid: boolean;
    reason: string;
}
export type Input = ContactSubmission;
export type Result = NormalizedContact;
export type Implementation = (input: Input) => Result | Promise<Result>;
