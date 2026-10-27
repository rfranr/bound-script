# NormalizeContact

Implement the contact normalization and validation functionality using the provided TypeScript contract.

The goal is to produce clean, consistent contact information that can be used reliably by other parts of the application.

## Expected behavior

- **Name:** Remove unnecessary whitespace while preserving the person's name, capitalization and international characters.
- **Email:** Normalize email addresses to lowercase, remove surrounding spaces and validate their basic structure.
- **Phone:** Normalize phone numbers into a consistent format, preserving international dialing prefixes when provided.
- **Validation:** Name, email and phone are required. Report all applicable validation errors using the error types defined in the contract.
- **Result:** Return the normalized contact when valid, or the validation errors when invalid.
- **Immutability:** Do not modify the original input.

## Implementation

You are free to choose the algorithms and internal structure.

Use the provided contract as the authoritative definition of the interface. Do not introduce additional business requirements or external dependencies.