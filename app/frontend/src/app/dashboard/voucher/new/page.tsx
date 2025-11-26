import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { VoucherCreateView } from 'src/sections/voucher/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Create a new user | Dashboard - ${CONFIG.appName}` };

export default function Page() {
  return <VoucherCreateView />;
}
