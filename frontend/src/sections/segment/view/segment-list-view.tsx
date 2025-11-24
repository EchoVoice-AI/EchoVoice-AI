'use client';

// Material-UI components
import Button from '@mui/material/Button';

// Routing
import { paths } from 'src/routes/paths';
import { RouterLink } from 'src/routes/components';

// Mock data and store
import { _userCards } from 'src/_mock';
import { DashboardContent } from 'src/layouts/dashboard';

import { Iconify } from 'src/components/iconify';
// UI Components
import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import { SegmentorCardList } from 'src/sections/segment/segmentor-card-list';
// Table components


export function SegmentListView() {
  return (
      <DashboardContent>
        <CustomBreadcrumbs
          heading="Segmentors List"
          links={[
            { name: 'Dashboard', href: paths.dashboard.root },
            { name: 'Segments', href: paths.dashboard.segments.root },
            { name: 'List' },
          ]}
          action={
            <Button
              component={RouterLink}
              href={paths.dashboard.segments.new}
              variant="contained"
              startIcon={<Iconify icon="mingcute:add-line" />}
            >
              New Segmentor
            </Button>
          }
          sx={{ mb: { xs: 3, md: 5 } }}
        />

        <SegmentorCardList users={_userCards} />
      </DashboardContent>
  );
}
