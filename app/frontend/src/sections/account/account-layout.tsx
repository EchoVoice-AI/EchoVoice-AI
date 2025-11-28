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

const NAV_ITEMS = [
  {
    label: 'General',
    icon: <Iconify width={24} icon="solar:user-id-bold" />,
    href: paths.dashboard.retrievers.settings,
  },
  {
    label: 'Index Configuration',
    icon: <Iconify width={24} icon="solar:settings-bold-duotone" />,
    href: `${paths.dashboard.retrievers.settings}/configuration`,
  },
  {
    label: 'Indexing Status',
    icon: <Iconify width={24} icon="solar:refresh-square-bold-duotone" />,
    href: `${paths.dashboard.retrievers.settings}/indexing-status`,
  },
  {
    label: 'Retrieval Logs',
    icon: <Iconify width={24} icon="solar:document-text-bold-duotone" />,
    href: `${paths.dashboard.retrievers.settings}/retrieval-logs`,
  },
  {
    label: 'API Keys & Access',
    icon: <Iconify width={24} icon="ic:round-vpn-key" />,
    href: `${paths.dashboard.retrievers.settings}/api-access`,
  },
];

// ----------------------------------------------------------------------

export function AccountLayout({ children, ...other }: DashboardContentProps) {
  const pathname = usePathname();

  return (
    <DashboardContent {...other}>
      <CustomBreadcrumbs
        heading="Retrievers Settings"
        links={[
          { name: 'Dashboard', href: paths.dashboard.root },
          { name: 'Retrievers', href: paths.dashboard.retrievers.root },
          { name: 'Settings' },
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
