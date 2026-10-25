/** A separate void-returning box implementation with a host-supplied output target. */
export function createDisplay(writeLine: (message: string) => void): (message: string) => void {
  return (message) => { writeLine(message); };
}
