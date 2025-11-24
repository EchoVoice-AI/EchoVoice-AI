import type { Metadata } from 'next';

import { _orders } from 'src/_mock/_order';
import { CONFIG } from 'src/global-config';

import { OrderDetailsView } from 'src/sections/order/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Order details | Dashboard - ${CONFIG.appName}` };

type Props = {
  params: { id: string };
};

export default function Page({ params }: Props) {
  const { id } = params;

  const currentOrder = _orders.find((order) => order.id === id);

  return <OrderDetailsView order={currentOrder} />;
}

// ----------------------------------------------------------------------

/**
 * [1] Default
 * Remove [1] and [2] if not using [2]
 * Will remove in Next.js v15
 */
const dynamic = CONFIG.isStaticExport ? 'auto' : 'force-dynamic';
export { dynamic };

/**
 * [2] Static exports
 * https://nextjs.org/docs/app/building-your-application/deploying/static-exports
 */
export async function generateStaticParams() {
  if (CONFIG.isStaticExport) {
    return _orders.map((order) => ({ id: order.id }));
  }
  return [];
}
