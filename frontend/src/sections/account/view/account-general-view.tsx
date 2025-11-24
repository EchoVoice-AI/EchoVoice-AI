'use client';

import { AccountGeneral } from '../account-general';

// ----------------------------------------------------------------------

export function AccountGeneralView({ customer }: { customer?: any }) {
  return <AccountGeneral customer={customer} />;
}
