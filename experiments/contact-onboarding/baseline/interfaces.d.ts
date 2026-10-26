// Conventional arm authority, manually prepared before any pilot outcome.
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
export interface WelcomeMessage {
    requestId: string;
    send: boolean;
    recipient: string;
    subject: string;
    html: string;
    reason: string;
}
export declare function normalize(submission: ContactSubmission): NormalizedContact | Promise<NormalizedContact>;
export declare function render(contact: NormalizedContact): WelcomeMessage | Promise<WelcomeMessage>;
