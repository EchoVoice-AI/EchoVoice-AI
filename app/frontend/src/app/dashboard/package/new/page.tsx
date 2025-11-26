import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { PackageCreateView } from 'src/sections/package/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Create a new user | Dashboard - ${CONFIG.appName}` };

export default function Page() {
  return <PackageCreateView />;
}
