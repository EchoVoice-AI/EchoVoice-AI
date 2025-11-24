'use client';

import type { ILeaveItem } from 'src/types/product';

import { paths } from 'src/routes/paths';

import { DashboardContent } from 'src/layouts/dashboard';

import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import { LeaveNewEditForm } from '../product-new-edit-form';

// ----------------------------------------------------------------------

type Props = {
  leave?: ILeaveItem;
};

export function ProductEditView({ leave }: Props) {
  return (
    <DashboardContent>
      <CustomBreadcrumbs
        heading="Edit"
        backHref={paths.dashboard.leave.root}
        links={[
          { name: 'Dashboard', href: paths.dashboard.root },
          { name: 'Leave', href: paths.dashboard.leave.root },
          { name: leave?.leave_type || '...' },
        ]}
        sx={{ mb: { xs: 3, md: 5 } }}
      />

      <LeaveNewEditForm currentLeave={leave} />
    </DashboardContent>
  );
}
