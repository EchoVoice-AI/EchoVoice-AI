'use client';

import type { ICustomerItem } from 'src/types/customer';

import { paths } from 'src/routes/paths';

import { DashboardContent } from 'src/layouts/dashboard';

import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import CustomerNewEditForm from '../customer-new-edit-form';


// ----------------------------------------------------------------------

type Props = {
  customer?: ICustomerItem;
};

export function CustomerEditView({ customer: currentCustomer }: Props) {
  return (
    <DashboardContent>
      <CustomBreadcrumbs
        heading="Edit"
        backHref={paths.dashboard.customer.list}
        links={[
          { name: 'Dashboard', href: paths.dashboard.root },
          { name: 'Customers', href: paths.dashboard.customer.root },
          { name: currentCustomer?.name },
        ]}
        sx={{ mb: { xs: 3, md: 5 } }}
      />

      <CustomerNewEditForm currentCustomer={currentCustomer} />
    </DashboardContent>
  );
}
