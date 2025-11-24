"use client";

import type { IUserCard } from 'src/types/user';
import type { Segment } from 'src/types/segmentor';

import { useState, useEffect } from 'react';

import Button from '@mui/material/Button';

import { paths } from 'src/routes/paths';
import { RouterLink } from 'src/routes/components';

import { fetcher, endpoints } from 'src/lib/axios';
import { DashboardContent } from 'src/layouts/dashboard';

import { Iconify } from 'src/components/iconify';
import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import { SegmentorCardList } from 'src/sections/segment/segmentor-card-list';

// ----------------------------------------------------------------------

function mapSegmentToUserCard(segment: Segment): IUserCard {
  const metadata = segment.metadata || {};

  return {
    id: segment.id,
    name: segment.name,
    role: metadata.role || '',
    coverUrl: metadata.coverUrl || metadata.cover || '',
    avatarUrl: metadata.avatarUrl || metadata.avatar || '',
    totalPosts: metadata.totalPosts ?? 0,
    totalFollowers: metadata.totalFollowers ?? 0,
    totalFollowing: metadata.totalFollowing ?? 0,
  };
}

export function SegmentListView() {
  const [users, setUsers] = useState<IUserCard[]>([]);

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      try {
        const data = await fetcher(endpoints.segmentor.list) as Segment[];

        if (!mounted) return;

        setUsers(data.map(mapSegmentToUserCard));
      } catch (error) {
        // keep working with empty list on error; log for debugging
        console.error('Failed to load segments:', error);
      }
    };

    load();

    return () => {
      mounted = false;
    };
  }, []);

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

      <SegmentorCardList users={users} />
    </DashboardContent>
  );
}
