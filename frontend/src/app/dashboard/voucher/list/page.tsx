import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { VoucherListView } from 'src/sections/voucher/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Package list | Dashboard - ${CONFIG.appName}` };

export default function Page() {
  return <VoucherListView />;
}
