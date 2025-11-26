import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { SegmentorCardsView } from 'src/sections/segment/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Segmentors | Dashboard - ${CONFIG.appName}` };
export default function Page() {
  return <SegmentorCardsView />;
}
