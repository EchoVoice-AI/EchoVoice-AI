import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { PackageListView } from 'src/sections/package/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Package list | Dashboard - ${CONFIG.appName}` };

export default function Page() {
  return <PackageListView />;
}
