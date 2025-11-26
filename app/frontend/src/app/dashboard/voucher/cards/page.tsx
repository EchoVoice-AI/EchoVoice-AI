import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { VoucherCardsView } from 'src/sections/voucher/view';



// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `User cards | Dashboard - ${CONFIG.appName}` };

export default function Page() {
  return <VoucherCardsView />;
}
