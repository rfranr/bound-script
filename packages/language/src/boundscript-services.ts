import {
  EmptyFileSystem,
  createDefaultCoreModule,
  createDefaultSharedCoreModule,
  inject,
  type LangiumCoreServices,
  type LangiumSharedCoreServices
} from 'langium';

import {
  BoundScriptGeneratedModule,
  BoundScriptGeneratedSharedModule
} from './generated/module.js';

export interface BoundScriptServices {
  readonly shared: LangiumSharedCoreServices;
  readonly language: LangiumCoreServices;
}

/** Creates the core services used by parsing today and reusable by a future LSP host. */
export function createBoundScriptServices(): BoundScriptServices {
  const shared = inject(
    createDefaultSharedCoreModule(EmptyFileSystem),
    BoundScriptGeneratedSharedModule
  );
  const language = inject(
    createDefaultCoreModule({ shared }),
    BoundScriptGeneratedModule
  );
  shared.ServiceRegistry.register(language);
  return { shared, language };
}
