import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { SegmentListView } from 'src/sections/segment/view/segment-list-view';


// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Segmentors list | Dashboard - ${CONFIG.appName}` };

export default function Page() {
  return <SegmentListView />;
}
