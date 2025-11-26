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
import { AppTopRelated } from '../app-top-related';
import { AppAreaInstalled } from '../app-area-installed';
import { AppWidgetSummary } from '../app-widget-summary';
import { AppCurrentDownload } from '../app-current-download';

// ----------------------------------------------------------------------

export function OverviewAppView() {
  const { user } = useMockedUser();

  const { leave_requests } = useDashStore();

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
              title="Total Active Users"
              percent={2.6}
              total={3654}
              chart={{
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                series: [15, 18, 12, 51, 68, 11, 39, 37],
              }}
            />)}
          {user?.role === 'employee' && (
            <AppWidgetSummary
              title="Total Active Users"
              percent={2.6}
              total={3654}
              chart={{
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                series: [15, 18, 12, 51, 68, 11, 39, 37],
              }}
            />)}
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          {user?.role === 'admin' && (
            <AppWidgetSummary
              title="Total Hotspot users"
              percent={0.2}
              total={2448}
              chart={{
                colors: [theme.palette.info.main],
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                series: [20, 41, 63, 33, 28, 35, 50, 46],
              }}
            />)}
          {user?.role === 'employee' && (
            <AppWidgetSummary
              title="Total Hotspot users"
              percent={0.2}
              total={2448}
              chart={{
                colors: [theme.palette.info.main],
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                series: [20, 41, 63, 33, 28, 35, 50, 46],
              }}
            />)}

        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          {user?.role === 'admin' && (
            <AppWidgetSummary
              title="Total PPPoE users"
              percent={-0.1}
              total={1206}
              chart={{
                colors: [theme.palette.error.main],
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                series: [18, 19, 31, 8, 16, 37, 12, 33],
              }}
            />)}
          {user?.role === 'employee' && (
            <AppWidgetSummary
              title="Total PPPoE users"
              percent={-0.1}
              total={1206}
              chart={{
                colors: [theme.palette.error.main],
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                series: [18, 19, 31, 8, 16, 37, 12, 33],
              }}
            />)}
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          {user?.role === 'admin' && (<AppCurrentDownload
            title="Client Distribution"
            subheader=""
            chart={{
              series: [
                { label: 'Hotspot', value: 2448 },
                { label: 'PPPoE', value: 1206 },
              ],
            }}
          />)}
          {user?.role === 'employee' && (
            <AppCurrentDownload
              title="Client Distribution"
              subheader=""
              chart={{
                series: [
                  { label: 'Hotspot', value: 2448 },
                  { label: 'PPPoE', value: 1206 },
                ],
              }}
            />)}
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 8 }}>
          {user?.role === 'admin' && (<AppAreaInstalled
            title="Sessions active monthly"
            subheader="(+43%) than last year"
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
                  name: '2022',
                  data: [
                    { name: 'Active', data: [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16] },
                    { name: 'Inactive', data: [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16] },
                  ],
                },
                {
                  name: '2023',
                  data: [
                    { name: 'Active', data: [6, 18, 14, 9, 20, 6, 22, 19, 8, 22, 8, 17] },
                    { name: 'Inactive', data: [6, 18, 14, 9, 20, 6, 22, 19, 8, 22, 8, 17] },
                  ],
                },
                {
                  name: '2024',
                  data: [
                    { name: 'Active', data: [6, 20, 15, 18, 7, 24, 6, 10, 12, 17, 18, 10] },
                    { name: 'Inactive', data: [6, 20, 15, 18, 7, 24, 6, 10, 12, 17, 18, 10] },
                  ],
                },
              ],
            }}
          />)}
          {user?.role === 'employee' && (
            <AppAreaInstalled
              title="Sessions active monthly"
              subheader="(+43%) than last year"
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
                    name: '2022',
                    data: [
                      { name: 'Active', data: [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16] },
                      { name: 'Inactive', data: [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16] },
                    ],
                  },
                  {
                    name: '2023',
                    data: [
                      { name: 'Active', data: [6, 18, 14, 9, 20, 6, 22, 19, 8, 22, 8, 17] },
                      { name: 'Inactive', data: [6, 18, 14, 9, 20, 6, 22, 19, 8, 22, 8, 17] },
                    ],
                  },
                  {
                    name: '2024',
                    data: [
                      { name: 'Active', data: [6, 20, 15, 18, 7, 24, 6, 10, 12, 17, 18, 10] },
                      { name: 'Inactive', data: [6, 20, 15, 18, 7, 24, 6, 10, 12, 17, 18, 10] },
                    ],
                  },
                ],
              }}
            />)}

        </Grid>

        <Grid size={{ xs: 12, lg: 8 }}>
          <AppNewInvoice
            title="Inbox"
            tableData={_appInvoices}
            headCells={[
              { id: 'id', label: 'Message ID' },
              { id: 'category', label: 'Type' },
              { id: 'price', label: 'Price' },
              { id: 'status', label: 'Status' },
              { id: '' },
            ]}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          {user?.role === 'admin' && (<AppTopRelated title="Leave applications" list={leave_requests} />)}
          {user?.role === 'employee' && (
            <AppTopRelated title="Related applications" list={leave_requests} />
          )}
        </Grid>



        <Grid size={{ xs: 12, md: 12, lg: 12 }}>
          <Box sx={{ gap: 3, display: 'flex', flexDirection: 'row' }}>
            <AppWidget
              title="Profile Completion"
              total={48}
              icon="solar:user-rounded-bold"
              chart={{ series: 48 }}
            />

            <AppWidget
              title="Applications"
              total={55566}
              icon="fluent:mail-24-filled"
              chart={{
                series: 75,
                colors: [theme.vars.palette.info.light, theme.vars.palette.info.main],
              }}
              sx={{ bgcolor: 'info.dark', [`& .${svgColorClasses.root}`]: { color: 'info.light' } }}
            />
          </Box>
        </Grid>
      </Grid>
    </DashboardContent>
  );
}
