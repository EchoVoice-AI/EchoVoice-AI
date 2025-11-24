import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { PackageCardsView } from 'src/sections/package/view';



// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `User cards | Dashboard - ${CONFIG.appName}` };

export default function Page() {
  return <PackageCardsView />;
}
