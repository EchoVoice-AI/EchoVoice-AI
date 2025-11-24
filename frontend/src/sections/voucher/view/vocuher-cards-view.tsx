'use client';

import Button from '@mui/material/Button';

import { paths } from 'src/routes/paths';
import { RouterLink } from 'src/routes/components';

import { _packages } from 'src/_mock/_package';
import { DashboardContent } from 'src/layouts/dashboard';

import { Iconify } from 'src/components/iconify';
import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import { VoucherCardList } from '../voucher-card-list';

// ----------------------------------------------------------------------

export function VoucherCardsView() {
  return (
    <DashboardContent>
      <CustomBreadcrumbs
        heading="Voucher cards"
        links={[
          { name: 'Dashboard', href: paths.dashboard.root },
          { name: 'Vouchers', href: paths.dashboard.voucher.root },
          { name: 'Cards' },
        ]}
        action={
          <Button
            component={RouterLink}
            href={paths.dashboard.voucher.new}
            variant="contained"
            startIcon={<Iconify icon="mingcute:add-line" />}
          >
            New voucher
          </Button>
        }
        sx={{ mb: { xs: 3, md: 5 } }}
      />

      <VoucherCardList vouchers={_packages} />
    </DashboardContent>
  );
}
