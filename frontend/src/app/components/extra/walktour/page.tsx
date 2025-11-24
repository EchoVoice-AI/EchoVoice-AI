import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { WalktourView } from 'src/sections/_examples/extra/walktour-view';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Walktour | Components - ${CONFIG.appName}` };

export default function Page() {
  return <WalktourView />;
}
