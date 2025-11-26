import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';
import { fetcher, endpoints } from 'src/lib/axios';

import { ProductDetailsView } from 'src/sections/product/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Leave details | Dashboard - ${CONFIG.appName}` };

type Props = {
  params: { id: string };
};

export default async function Page({ params }: Props) {
  const { id } = params;

  const  leave  = await getProduct(id);


  return <ProductDetailsView product={leave} />;
}

// ----------------------------------------------------------------------

async function getProduct(id: string) {
  const URL = id ? `${endpoints.leave.details}${id}` : '';

  try {
    const data = await fetcher(URL); // Await the fetcher response
    return data;
  } catch (error) {
    console.error('Error fetching product:', error);
    return null;
  }
}


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
//  */
export async function generateStaticParams() {
  if (CONFIG.isStaticExport) {
    const URL = `${endpoints.leave.list}`;

    try {
      const data = await fetcher(URL); // Await the fetcher response
      return data.map((product: { id: string }) => ({ id: product.id }));
    } catch (error) {
      console.error('Error fetching product:', error);
      return [];
    }
  }
  return [];
}

