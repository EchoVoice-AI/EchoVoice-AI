'use client';

import { paths } from 'src/routes/paths';

import { DashboardContent } from 'src/layouts/dashboard';

import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import { LeaveNewEditForm } from '../product-new-edit-form';

// ----------------------------------------------------------------------

export function ProductCreateView() {
  return (
    <DashboardContent>
      <CustomBreadcrumbs
        heading="Apply for leave"
        links={[
          { name: 'Dashboard', href: paths.dashboard.root },
          { name: 'Leave', href: paths.dashboard.leave.root },
          { name: 'New leave application' },
        ]}
        sx={{ mb: { xs: 3, md: 5 } }}
      />

      <LeaveNewEditForm />
    </DashboardContent>
  );
}
