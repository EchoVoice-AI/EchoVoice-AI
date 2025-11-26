'use client';

import Button from '@mui/material/Button';

import { paths } from 'src/routes/paths';
import { RouterLink } from 'src/routes/components';

import { _packages } from 'src/_mock/_package';
import { DashboardContent } from 'src/layouts/dashboard';

import { Iconify } from 'src/components/iconify';
import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import { PackageCardList } from '../package-card-list';

// ----------------------------------------------------------------------

export function PackageCardsView() {
  return (
    <DashboardContent>
      <CustomBreadcrumbs
        heading="Package cards"
        links={[
          { name: 'Dashboard', href: paths.dashboard.root },
          { name: 'Packages', href: paths.dashboard.package.root },
          { name: 'Cards' },
        ]}
        action={
          <Button
            component={RouterLink}
            href={paths.dashboard.package.new}
            variant="contained"
            startIcon={<Iconify icon="mingcute:add-line" />}
          >
            New package
          </Button>
        }
        sx={{ mb: { xs: 3, md: 5 } }}
      />

      <PackageCardList packages={_packages} />
    </DashboardContent>
  );
}
