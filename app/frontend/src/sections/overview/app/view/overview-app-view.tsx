'use client';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';
import Button from '@mui/material/Button';
import { useTheme } from '@mui/material/styles';

import { _appFeatured, _appInvoices } from 'src/_mock';
import { useDashStore } from 'src/store/dashboardSttore';
import { DashboardContent } from 'src/layouts/dashboard';
import { SeoIllustration } from 'src/assets/illustrations';

import { svgColorClasses } from 'src/components/svg-color';

import { useMockedUser } from 'src/auth/hooks';

import { AppWidget } from '../app-widget';
import { AppWelcome } from '../app-welcome';
import { AppFeatured } from '../app-featured';
import { AppNewInvoice } from '../app-new-invoice';
import { AppAreaInstalled } from '../app-area-installed';
import { AppWidgetSummary } from '../app-widget-summary';
import { AppCurrentDownload } from '../app-current-download';

// ----------------------------------------------------------------------

export function OverviewAppView() {
  const { user } = useMockedUser();
  const theme = useTheme();

  return (
    <DashboardContent maxWidth="xl">
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 8 }}>
          <AppWelcome
            title={`Welcome back 👋 \n ${user?.displayName}`}
            description="Fill your Profile to get started"
            img={<SeoIllustration hideBackground />}
            action={
              <Button variant="contained" color="primary" href='user/'>
                Profile
              </Button>
            }
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppFeatured list={_appFeatured} />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
  {user?.role === 'admin' && (
    <AppWidgetSummary
      title="Avg. Conversion Uplift (%)"
      percent={2.6} // Percentage change from previous period
      total={9.8} // The average conversion lift achieved (e.g., 9.8%)
      chart={{
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
        series: [5.1, 7.8, 6.2, 9.1, 8.8, 10.1, 9.9, 10.5], // Conversion uplift trend
      }}
    />)}
  {user?.role === 'employee' && (
    <AppWidgetSummary
      title="Avg. Conversion Uplift (%)"
      percent={2.6}
      total={9.8}
      chart={{
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
        series: [5.1, 7.8, 6.2, 9.1, 8.8, 10.1, 9.9, 10.5],
      }}
    />)}
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          {user?.role === 'admin' && (
            <AppWidgetSummary
              title="Messages Blocked by Safety Agent"
              percent={-5.2} // A negative change is good (fewer violations)
              total={2448} // Total number of messages blocked by Phase 4 agent
              chart={{
                colors: [theme.palette.info.main],
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                series: [320, 290, 260, 310, 350, 280, 240, 190], // Trend of blocked messages
              }}
            />)}
          {user?.role === 'employee' && (
            <AppWidgetSummary
              title="Messages Blocked by Safety Agent"
              percent={-5.2}
              total={2448}
              chart={{
                colors: [theme.palette.info.main],
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                series: [320, 290, 260, 310, 350, 280, 240, 190],
              }}
            />)}

        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          {user?.role === 'admin' && (
            <AppWidgetSummary
              title="Active Agent Workflows"
              percent={15.3} // Positive growth in system usage
              total={1206} // Total active orchestration loops (LangGraph instances)
              chart={{
                colors: [theme.palette.success.main], // Switched to success color for growth
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                series: [800, 850, 920, 1050, 1100, 1200, 1250, 1310], // Trend of active workflows
              }}
            />)}
          {user?.role === 'employee' && (
            <AppWidgetSummary
              title="Active Agent Workflows"
              percent={15.3}
              total={1206}
              chart={{
                colors: [theme.palette.success.main],
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                series: [800, 850, 920, 1050, 1100, 1200, 1250, 1310],
              }}
            />)}
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
        {user?.role === 'admin' && (
          <AppCurrentDownload
            title="Active Segment Distribution"
            subheader="Allocation of messages by high-value segment"
            chart={{
              series: [
                // Repurposed from 'Hotspot' and 'PPPoE' to relevant segments
                { label: 'High-Value Shopper', value: 2448 },
                { label: 'Budget-Conscious', value: 1206 },
                { label: 'Loyalty Program Member', value: 950 },
                { label: 'Recent Service Interactor', value: 500 },
              ],
            }}
          />)}
        {user?.role === 'employee' && (
          <AppCurrentDownload
            title="Active Segment Distribution"
            subheader="Allocation of messages by high-value segment"
            chart={{
              series: [
                { label: 'High-Value Shopper', value: 2448 },
                { label: 'Budget-Conscious', value: 1206 },
                { label: 'Loyalty Program Member', value: 950 },
                { label: 'Recent Service Interactor', value: 500 },
              ],
            }}
          />)}
      </Grid>

      <Grid size={{ xs: 12, md: 6, lg: 8 }}>
        {user?.role === 'admin' && (
          <AppAreaInstalled
            title="Workflow Compliance Status (Monthly)"
            subheader="Tracking message approval rates by the Safety Agent"
            chart={{
              categories: [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
              ],
              series: [
                {
                  name: '2024',
                  data: [
                    { name: 'Approved', data: [92, 95, 213, 421, 94, 95, 196, 95, 93, 94, 95, 96] },
                    { name: 'Blocked', data: [758, 15, 7, 29, 226, 5, 34, 85, 47, 26, 65, 64] },
                  ],
                },
                {
                  name: '2025',
                  data: [
                    { name: 'Approved', data: [494, 296, 395, 427, 96, 198, 297, 98, 596, 97, 98, 99] },
                    { name: 'Blocked', data: [86, 34, 35, 23, 124, 92, 13, 2, 34, 63, 22, 1] },
                  ],
                },
              ],
            }}
          />)}
        {user?.role === 'employee' && (
          <AppAreaInstalled
            title="Workflow Compliance Status (Monthly)"
            subheader="Tracking message approval rates by the Safety Agent"
            chart={{
              categories: [
                'Jan',
                'Feb',
                'Mar',
                'Apr',
                'May',
                'Jun',
                'Jul',
                'Aug',
                'Sep',
                'Oct',
                'Nov',
                'Dec',
              ],
              series: [
                {
                  name: '2023',
                  data: [
                    { name: 'Approved', data: [92, 95, 93, 91, 94, 95, 96, 95, 93, 94, 95, 96] },
                    { name: 'Blocked', data: [8, 5, 7, 9, 6, 5, 4, 5, 7, 6, 5, 4] },
                  ],
                },
                {
                  name: '2024',
                  data: [
                    { name: 'Approved', data: [94, 96, 95, 97, 96, 98, 97, 98, 96, 97, 98, 99] },
                    { name: 'Blocked', data: [6, 4, 5, 3, 4, 2, 3, 2, 4, 3, 2, 1] },
                  ],
                },
              ],
            }}
          />)}
      </Grid>
        <Grid size={{ xs: 12, lg: 8 }}>
        <AppNewInvoice
          // Changed title from "Inbox" to reflect a real-time log of agent activity
          title="Orchestration Log & Safety Audit"
          // Assuming _appInvoices is replaced with an array of log entries or messages
          tableData={_appInvoices} 
          headCells={[
            // Renamed for context: Message ID -> Message/Task ID
            { id: 'id', label: 'Task ID' },
            // Renamed for context: Category -> Agent/Phase
            { id: 'category', label: 'Agent/Phase' },
            // Renamed for context: Price -> Compliance Score (or Uplift Score)
            { id: 'price', label: 'Compliance Score' },
            // Status is perfect, but context changed (e.g., Blocked, Approved, Rewritten)
            { id: 'status', label: 'Status' },
            { id: '' },
          ]}
        />
      </Grid>




      <Grid size={{ xs: 12, md: 12, lg: 12 }}>
        <Box sx={{ gap: 3, display: 'flex', flexDirection: 'row',justifyContent: 'space-around' }}>
          <AppWidget
            // Changed title from "Profile Completion" to a core RAG metric
            title="Product Content Coverage"
            total={92} // Total percentage of product content indexed
            icon="solar:archive-bold-duotone"
            chart={{ series: 92 }} // Use chart to visually represent coverage
          />

          <AppWidget
            // Changed title from "Applications" to a key performance metric
            title="Experimentation Simulator Runs"
            total={556} // Total number of A/B/n simulations or experiments run
            icon="fluent:rocket-24-filled"
            chart={{
              series: 85, // Representative of the total possible number of runs
              colors: [theme.vars.palette.success.light, theme.vars.palette.success.main],
            }}
            sx={{ bgcolor: 'success.dark', [`& .${svgColorClasses.root}`]: { color: 'success.light' } }}
          />
        </Box>
      </Grid>
      </Grid>
    </DashboardContent>
  );
}
