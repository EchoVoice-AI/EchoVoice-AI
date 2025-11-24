'use client';

import { paths } from 'src/routes/paths';

import { DashboardContent } from 'src/layouts/dashboard';

import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import { VoucherNewEditForm } from '../voucher-new-edit-form';

// ----------------------------------------------------------------------

export function VoucherCreateView() {
  return (
    <DashboardContent>
      <CustomBreadcrumbs
        heading="Create a new voucher"
        links={[
          { name: 'Dashboard', href: paths.dashboard.root },
          { name: 'Vouchers', href: paths.dashboard.voucher.root },
          { name: 'New voucher' },
        ]}
        sx={{ mb: { xs: 3, md: 5 } }}
      />

      <VoucherNewEditForm />
    </DashboardContent>
  );
}
