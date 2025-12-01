'use client';

import { useState } from 'react';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';

import { DashboardContent } from 'src/layouts/dashboard';
import { _segmentors, _segmentorReview, _segmentorsOverview } from 'src/_mock';
import {
  BookingIllustration,
  CheckInIllustration,
  CheckoutIllustration,
} from 'src/assets/illustrations';

import { SegmentorCardList } from 'src/sections/segment/segmentor-card-list';

import { BookingBooked } from '../booking-booked';
import { BookingTotalIncomes } from '../booking-total-incomes';
import { BookingWidgetSummary } from '../booking-widget-summary';
import { BookingCheckInWidgets } from '../booking-check-in-widgets';
import { BookingCustomerReviews } from '../booking-customer-reviews';


// ----------------------------------------------------------------------

export function OverviewBookingView() {
  // Use mock segments data and keep local state so updates persist in-memory
  const [segments, setSegments] = useState(() => _segmentors.slice());

  const handleUpdateSegment = (updated: any) => {
    setSegments((prev) => prev.map((s) => (s.id === updated.id ? { ...s, ...updated } : s)));
  };

  const totalActive = segments.length;

  // Try to derive rule-based vs experiment counts from common keys.
  const totalRuleBased = segments.filter((s: any) => {
    const val = ((s.type ) || '').toString().toLowerCase();
    return val.includes('rule') || val.includes('rule-based');
  }).length;

  const totalExperiment = segments.filter((s: any) => {
    const val = ((s.type ) || '').toString().toLowerCase();
    return val.includes('experiment') || val.includes('hotspot');
  }).length;

  return (
    <DashboardContent maxWidth="xl">
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 4 }}>
                <BookingWidgetSummary
                  title="Total Segments"
                  percent={0}
                  total={totalActive}
                  icon={<BookingIllustration />}
                />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <BookingWidgetSummary
            title="Rule-based Segments"
            percent={0}
            total={totalRuleBased}
            icon={<CheckInIllustration />}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <BookingWidgetSummary
            title="Experiment Segments"
            percent={0}
            total={totalExperiment}
            icon={<CheckoutIllustration />}
          />
        </Grid>

        <Grid container size={12}>
          <Grid size={{ xs: 12, md: 7, lg: 8 }}>
            <Box
              sx={{
                mb: 3,
                p: { md: 1 },
                display: 'flex',
                gap: { xs: 3, md: 1 },
                borderRadius: { md: 2 },
                flexDirection: 'column',
                bgcolor: { md: 'background.neutral' },
              }}
            >
              <Box
                sx={{
                  p: { md: 1 },
                  display: 'grid',
                  gap: { xs: 3, md: 0 },
                  borderRadius: { md: 2 },
                  bgcolor: { md: 'background.paper' },
                  gridTemplateColumns: { xs: 'repeat(1, 1fr)', md: 'repeat(2, 1fr)' },
                }}
              >
                <BookingTotalIncomes
                  title="Total segments"
                  total={totalActive}
                  percent={2.6}
                  chart={{
                    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
                    series: [{ data: [10, 41, 80, 100, 60, 120, 69, 91, 160] }],
                  }}
                />

                <BookingBooked
                  title="Segment Status"
                  data={_segmentorsOverview}
                  sx={{ boxShadow: { md: 'none' } }}
                />
              </Box>

              <BookingCheckInWidgets
                chart={{
                  series: [
                    {
                      label: 'Rule-based Segments',
                      percent: totalActive ? Number(((totalRuleBased / totalActive) * 100).toFixed(1)) : 0,
                      total: totalRuleBased,
                    },
                    {
                      label: 'Experiment Segments',
                      percent: totalActive ? Number(((totalExperiment / totalActive) * 100).toFixed(1)) : 0,
                      total: totalExperiment,
                    },
                  ],
                }}
                sx={{ boxShadow: { md: 'none' } }}
              />
            </Box>
          </Grid>

          <Grid size={{ xs: 12, md: 5, lg: 4 }}>
            <Box sx={{ gap: 3, display: 'flex', flexDirection: 'column' }}>
              <BookingCustomerReviews
                title="Audit entries"
                subheader={`${_segmentorReview.length} entries`}
                list={_segmentorReview}
              />
            </Box>
          </Grid>
        </Grid>

        <Grid size={12}>
          <SegmentorCardList segments={segments} onUpdate={handleUpdateSegment} />
        </Grid>
      </Grid>
      
    </DashboardContent>
  );
}
