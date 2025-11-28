'use client';

import { varAlpha } from 'minimal-shared/utils';

import Box from '@mui/material/Box';
import { cardClasses } from '@mui/material/Card';
import Typography from '@mui/material/Typography';

import { CONFIG } from 'src/global-config';
import { DashboardContent } from 'src/layouts/dashboard';
// NOTE: These mock imports need to be replaced with RAG-specific mock data (e.g., _ragCitationsFeatured, _ragIndexWarnings)
import { _coursesContinue, _coursesFeatured, _coursesReminder } from 'src/_mock'; 

import { useAuthContext } from 'src/auth/hooks/use-auth-context';

// Keep the original component imports but change the context of what they display
import { CourseProgress } from '../course-progress';
import { CourseContinue } from '../course-continue';
import { CourseFeatured } from '../course-featured';
import { CourseReminders } from '../course-reminders';
import { CourseMyAccount } from '../course-my-account';
import { CourseHoursSpent } from '../course-hours-spent';
import { CourseMyStrength } from '../course-my-strength';
import { CourseWidgetSummary } from '../course-widget-summary';

// ----------------------------------------------------------------------

export function OverviewRetrieverView() { // Renamed View component for context
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
            <Typography
              sx={{ color: 'text.secondary' }}
            >Review the health and performance of your **Content Retriever Index**!</Typography> {/* Changed secondary text */}
          </Box>

          <Box
            sx={{
              gap: 3,
              display: 'grid',
              gridTemplateColumns: { xs: 'repeat(1, 1fr)', md: 'repeat(3, 1fr)' },
            }}
          >
            <CourseWidgetSummary // Widget 1: Total Content Indexed
              title="Total Indexed Documents"
              total={6540} // Total number of documents indexed
              icon={`${CONFIG.assetsDir}/assets/icons/rag/ic-documents.svg`}
            />

            <CourseWidgetSummary // Widget 2: Successful Retrieval Rate
              title="Successful Retrieval Rate (%)"
              total={93.5}
              color="success"
              icon={`${CONFIG.assetsDir}/assets/icons/rag/ic-relevance.svg`}
            />

            <CourseWidgetSummary // Widget 3: Index Stale Rate
              title="Index Stale Rate (%)"
              total={2.5}
              color="secondary"
              icon={`${CONFIG.assetsDir}/assets/icons/rag/ic-stale.svg`}
            />
          </Box>

          <CourseHoursSpent // Chart 1: Retrieval Latency
            title="Avg. Content Retrieval Latency (ms)"
            chart={{
              series: [
                {
                  name: 'Weekly',
                  categories: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
                  data: [{ data: [110, 85, 95, 120, 105] }], // Mock data in milliseconds
                },
                {
                  name: 'Monthly',
                  categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
                  data: [{ data: [93, 112, 119, 88, 103, 112, 114, 108, 93] }],
                },
                {
                  name: 'Yearly',
                  categories: ['2023', '2024'],
                  data: [{ data: [80, 100] }],
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
            <CourseProgress // Chart 2: Retrieval Success Breakdown
              title="RAG Retrieval Status Breakdown"
              chart={{
                series: [
                  { label: 'Successful Citation', value: 75 },
                  { label: 'Low Relevance Score', value: 15 },
                  { label: 'Retrieval Failure', value: 10 },
                ],
              }}
            />

            <CourseContinue // List 1: Latest Indexed Content
              title="Latest Indexed Content" 
              list={_coursesContinue} // Assuming this list now holds recent indexed document titles
            />
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
          <CourseMyAccount /> {/* Component (3) - Kept as placeholder for Index Metadata/Settings */}

          <CourseMyStrength // Chart 3: Relevance by Content Category
            title="Query Relevance by Content Category"
            chart={{
              categories: ['Segments', 'Product Specs', 'Legal Rules', 'Pricing', 'T&Cs'],
              series: [{ data: [85, 92, 78, 90, 65] }], // Relevance scores
            }}
          />

          <CourseReminders // List 4: Index Health Warnings
            title="Index Health Warnings" 
            list={_coursesReminder} // Assuming this list now holds warnings (e.g., stale index, low coverage)
          />
        </Box>
      </Box>
    </DashboardContent>
  );
}