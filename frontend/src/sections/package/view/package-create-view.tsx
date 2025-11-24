'use client';

import { paths } from 'src/routes/paths';

import { DashboardContent } from 'src/layouts/dashboard';

import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import { PackageNewEditForm } from '../package-new-edit-form';

// ----------------------------------------------------------------------

export function PackageCreateView() {
  return (
    <DashboardContent>
      <CustomBreadcrumbs
        heading="Create a new package"
        links={[
          { name: 'Dashboard', href: paths.dashboard.root },
          { name: 'Packages', href: paths.dashboard.package.root },
          { name: 'New package' },
        ]}
        sx={{ mb: { xs: 3, md: 5 } }}
      />

      <PackageNewEditForm />
    </DashboardContent>
  );
}
