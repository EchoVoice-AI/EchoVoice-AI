'use client';

import { varAlpha } from 'minimal-shared/utils';

import Box from '@mui/material/Box';
import { cardClasses } from '@mui/material/Card';
import Typography from '@mui/material/Typography';

import { CONFIG } from 'src/global-config';
import { DashboardContent } from 'src/layouts/dashboard';
// Reuse mock lists for now; replace with generation-specific mocks later if needed
import { _coursesContinue, _coursesFeatured, _coursesReminder } from 'src/_mock';

import { useAuthContext } from 'src/auth/hooks/use-auth-context';

// Reuse existing course components for layout; generation-specific naming shown in labels
import { CourseProgress } from '../../course/course-progress';
import { CourseContinue } from '../../course/course-continue';
import { CourseFeatured } from '../../course/course-featured';
import { CourseReminders } from '../../course/course-reminders';
import { CourseMyAccount } from '../../course/course-my-account';
import { CourseHoursSpent } from '../../course/course-hours-spent';
import { CourseMyStrength } from '../../course/course-my-strength';
import { CourseWidgetSummary } from '../../course/course-widget-summary';

// ----------------------------------------------------------------------

export function OverviewGenerationView() {
  const { user } = useAuthContext();
  return (
    <DashboardContent
      maxWidth={false}
      disablePadding
      sx={[
        (theme) => ({
          borderTop: { lg: `solid 1px ${varAlpha(theme.vars.palette.grey['500Channel'], 0.12)}` },
        }),
      ]}
    >
      <Box sx={{ display: 'flex', flex: '1 1 auto', flexDirection: { xs: 'column', lg: 'row' } }}>
        <Box
          sx={[
            (theme) => ({
              gap: 3,
              display: 'flex',
              minWidth: { lg: 0 },
              py: { lg: 3, xl: 5 },
              flexDirection: 'column',
              flex: { lg: '1 1 auto' },
              px: { xs: 2, sm: 3, xl: 5 },
              borderRight: {
                lg: `solid 1px ${varAlpha(theme.vars.palette.grey['500Channel'], 0.12)}`,
              },
            }),
          ]}
        >
          <Box sx={{ mb: 2 }}>
            <Typography variant="h4" sx={{ mb: 1 }}>
              Hi, {user?.first_name}👋
            </Typography>
            <Typography sx={{ color: 'text.secondary' }}>
              Review the runtime metrics and quality signals for your Generation models and pipelines.
            </Typography>
          </Box>

          <Box
            sx={{
              gap: 3,
              display: 'grid',
              gridTemplateColumns: { xs: 'repeat(1, 1fr)', md: 'repeat(3, 1fr)' },
            }}
          >
            <CourseWidgetSummary
              title="Total Generated Outputs"
              total={124300}
              icon={`${CONFIG.assetsDir}/assets/icons/generation/ic-outputs.svg`}
            />

            <CourseWidgetSummary
              title="Avg. Generation Latency (ms)"
              total={420}
              color="warning"
              icon={`${CONFIG.assetsDir}/assets/icons/generation/ic-latency.svg`}
            />

            <CourseWidgetSummary
              title="Hallucination Rate (%)"
              total={1.8}
              color="error"
              icon={`${CONFIG.assetsDir}/assets/icons/generation/ic-hallucination.svg`}
            />
          </Box>

          <CourseHoursSpent
            title="Avg. Generation Latency (ms) — Time Series"
            chart={{
              series: [
                {
                  name: 'Hourly',
                  categories: ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'],
                  data: [{ data: [380, 420, 410, 450, 400, 430] }],
                },
                {
                  name: 'Daily',
                  categories: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                  data: [{ data: [400, 410, 420, 430, 415, 405, 395] }],
                },
              ],
            }}
          />

          <Box
            sx={{
              gap: 3,
              display: 'grid',
              alignItems: 'flex-start',
              gridTemplateColumns: { xs: 'repeat(1, 1fr)', md: 'repeat(2, 1fr)' },
            }}
          >
            <CourseProgress
              title="Generation Quality Breakdown"
              chart={{
                series: [
                  { label: 'High Quality', value: 82 },
                  { label: 'Acceptable', value: 12 },
                  { label: 'Low Quality / Hallucination', value: 6 },
                ],
              }}
            />

            <CourseContinue title="Recent Prompts & Outputs" list={_coursesContinue} />
          </Box>
        </Box>

        <Box
          sx={{
            width: 1,
            display: 'flex',
            flexDirection: 'column',
            px: { xs: 2, sm: 3, xl: 5 },
            pt: { lg: 8, xl: 10 },
            pb: { xs: 8, xl: 10 },
            flexShrink: { lg: 0 },
            gap: { xs: 3, lg: 5, xl: 8 },
            maxWidth: { lg: 320, xl: 360 },
            bgcolor: { lg: 'background.neutral' },
            [`& .${cardClasses.root}`]: {
              p: { xs: 3, lg: 0 },
              boxShadow: { lg: 'none' },
              bgcolor: { lg: 'transparent' },
            },
          }}
        >
          <CourseMyAccount /> {/* Placeholder for Model Metadata / Endpoint Info */}

          <CourseMyStrength
            title="Relevance / Quality by Category"
            chart={{
              categories: ['Instructions', 'Code', 'Summaries', 'Conversations'],
              series: [{ data: [88, 75, 92, 80] }],
            }}
          />

          <CourseReminders title="Generation Alerts" list={_coursesReminder} />
        </Box>
      </Box>
    </DashboardContent>
  );
}
