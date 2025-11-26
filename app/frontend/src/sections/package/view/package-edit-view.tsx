'use client';

import type { IPackageItem } from 'src/types/package';

import { paths } from 'src/routes/paths';

import { DashboardContent } from 'src/layouts/dashboard';

import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import { PackageNewEditForm } from '../package-new-edit-form';

// ----------------------------------------------------------------------

type Props = {
  package?: IPackageItem;
};

export function PackageEditView({ package: currentPackage }: Props) {
  return (
    <DashboardContent>
      <CustomBreadcrumbs
        heading="Edit"
        backHref={paths.dashboard.package.list}
        links={[
          { name: 'Dashboard', href: paths.dashboard.root },
          { name: 'Packages', href: paths.dashboard.package.root },
          { name: currentPackage?.name },
        ]}
        sx={{ mb: { xs: 3, md: 5 } }}
      />

      <PackageNewEditForm currentPackage={currentPackage} />
    </DashboardContent>
  );
}
