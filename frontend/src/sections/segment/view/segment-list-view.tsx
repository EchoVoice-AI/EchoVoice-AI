"use client";

import type { Segment, ISegmentorCard } from 'src/types/segmentor';

import useSWR from 'swr';

import Button from '@mui/material/Button';

import { paths } from 'src/routes/paths';
import { RouterLink } from 'src/routes/components';

import { _mock } from 'src/_mock';
import { fetcher, endpoints } from 'src/lib/axios';
import { DashboardContent } from 'src/layouts/dashboard';

import { Iconify } from 'src/components/iconify';
import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import { SegmentorCardList } from 'src/sections/segment/segmentor-card-list';

// ----------------------------------------------------------------------


export function SegmentListView() {
  const { data, error, isLoading } = useSWR<Segment[]>(endpoints.segmentor.list, fetcher);

  const segments: ISegmentorCard[] = (data || []).map((segment, index) => ({
    id: segment.id,
    name: segment.name,
    priority: segment.priority,
    role: (segment.metadata || {}).role || '',
    metadata: segment.metadata || {},
    avatarUrl: '',
    coverUrl: _mock.image.cover(index),
    enabled: segment.enabled,
  }));

  if (error) {
    console.error('Failed to load segments:', error);
  }

  return (
    <DashboardContent>
      <CustomBreadcrumbs
        heading="Segmentor Node List"
        links={[
          { name: 'Dashboard', href: paths.dashboard.root },
          { name: 'Segmentors', href: paths.dashboard.segments.root },
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

      <SegmentorCardList segments={segments} />
    </DashboardContent>
  );
}
