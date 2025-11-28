import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { OverviewRetrieverView } from 'src/sections/overview/course/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Retrievers | Dashboard - ${CONFIG.appName}` };

export default function Page() {
  return <OverviewRetrieverView />;
}
