'use client';

import type { DashboardContentProps } from 'src/layouts/dashboard';

import { removeLastSlash } from 'minimal-shared/utils';

import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';

import { paths } from 'src/routes/paths';
import { usePathname } from 'src/routes/hooks';
import { RouterLink } from 'src/routes/components';

import { DashboardContent } from 'src/layouts/dashboard';

import { Iconify } from 'src/components/iconify';
import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

// ----------------------------------------------------------------------


function getNavItems(customerId: string) {
  const base = `${paths.dashboard.customer.root}/${customerId}/account`;
  return [
    {
      label: 'General',
      icon: <Iconify width={24} icon="solar:user-id-bold" />,
      href: base,
    },
    {
      label: 'Billing',
      icon: <Iconify width={24} icon="solar:bill-list-bold" />,
      href: `${base}/billing`,
    },
    {
      label: 'Notifications',
      icon: <Iconify width={24} icon="solar:bell-bing-bold" />,
      href: `${base}/notifications`,
    },
    {
      label: 'Social links',
      icon: <Iconify width={24} icon="solar:share-bold" />,
      href: `${base}/socials`,
    },
    {
      label: 'Security',
      icon: <Iconify width={24} icon="ic:round-vpn-key" />,
      href: `${base}/change-password`,
    },
  ];
}

// ----------------------------------------------------------------------

// Accept customerId as prop
export function AccountLayout({ customerId, children, ...other }: DashboardContentProps & { customerId: string }) {
  const pathname = usePathname();
  const NAV_ITEMS = getNavItems(customerId);

  return (
    <DashboardContent {...other}>
      <CustomBreadcrumbs
        heading="Account"
        links={[
          { name: 'Dashboard', href: paths.dashboard.root },
          { name: 'User', href: paths.dashboard.customer.root },
          { name: 'Account' },
        ]}
        sx={{ mb: 3 }}
      />

      <Tabs value={removeLastSlash(pathname)} sx={{ mb: { xs: 3, md: 5 } }}>
        {NAV_ITEMS.map((tab) => (
          <Tab
            component={RouterLink}
            key={tab.href}
            label={tab.label}
            icon={tab.icon}
            value={tab.href}
            href={tab.href}
          />
        ))}
      </Tabs>

      {children}
    </DashboardContent>
  );
}
