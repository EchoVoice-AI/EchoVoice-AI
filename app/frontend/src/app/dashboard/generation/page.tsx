import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { OverviewGenerationView } from 'src/sections/overview/generation/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Generation | Dashboard - ${CONFIG.appName}` };

export default function Page() {
  return <OverviewGenerationView />;
}
