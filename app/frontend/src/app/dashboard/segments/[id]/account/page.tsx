import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { AccountGeneralView } from 'src/sections/customer/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = {
  title: `Account general settings | Dashboard - ${CONFIG.appName}`,
};

type Props = {
  params: { id: string };
};

import { _customerList } from 'src/_mock/_customerList';

export default function Page({ params }: Props) {
  const { id } = params;
  return <AccountGeneralView id={id} />;
}
