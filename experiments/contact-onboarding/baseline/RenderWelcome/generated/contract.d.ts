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
export interface WelcomeMessage {
    requestId: string;
    send: boolean;
    recipient: string;
    subject: string;
    html: string;
    reason: string;
}
export type Input = NormalizedContact;
export type Result = WelcomeMessage;
export type Implementation = (input: Input) => Result | Promise<Result>;
