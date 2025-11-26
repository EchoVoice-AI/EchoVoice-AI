'use client';

import type { ILeaveBalance, ILeaveTableFilters } from 'src/types/product';
import type {
    GridColDef,
    GridRowSelectionModel,
    GridColumnVisibilityModel,
} from '@mui/x-data-grid';

import { useState, useEffect } from 'react';
import { useBoolean, useSetState } from 'minimal-shared/hooks';

import Card from '@mui/material/Card';
import {
    DataGrid,
    gridClasses,
} from '@mui/x-data-grid';

import { paths } from 'src/routes/paths';

import { DashboardContent } from 'src/layouts/dashboard';
import { useGetLeaveBalances } from 'src/actions/product';

import { EmptyContent } from 'src/components/empty-content';
import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import {
    RenderCellBalance,
    RenderCellUsedDays,
    RenderCellTotalDays,
    RenderCellBalanceType,
    RenderCellRemainingDays,
} from '../product-table-row';

// ----------------------------------------------------------------------

const PUBLISH_OPTIONS = [
    { value: 'approved', label: 'Approved' },
    { value: 'pending', label: 'Pending' },
    { value: 'rejected', label: 'Rejected' },
];

const HIDE_COLUMNS = { category: false };

const HIDE_COLUMNS_TOGGLABLE = ['category', 'actions'];

// ----------------------------------------------------------------------

export function LeaveBalanceListView() {
    const confirmDialog = useBoolean();

    const { balances, balancesLoading } = useGetLeaveBalances();

    const [tableData, setTableData] = useState<ILeaveBalance[]>(balances);
    const [selectedRowIds, setSelectedRowIds] = useState<GridRowSelectionModel>([]);
    const [filterButtonEl, setFilterButtonEl] = useState<HTMLButtonElement | null>(null);

    const filters = useSetState<ILeaveTableFilters>({ leave_type: [], status: [] });
    const { state: currentFilters } = filters;

    const [columnVisibilityModel, setColumnVisibilityModel] =
        useState<GridColumnVisibilityModel>(HIDE_COLUMNS);

    useEffect(() => {
        if (balances.length) {
            setTableData(balances);
        }
    }, [balances]);

    const canReset = currentFilters.leave_type.length > 0 || currentFilters.status.length > 0;



    const columns: GridColDef[] = [

        {
            field: 'employee_name',
            headerName: 'Employee Name',
            flex: 1,
            minWidth: 360,
            hideable: false,
            renderCell: (params) => (
                <RenderCellBalance params={params} href={paths.dashboard.leave.details(params.row.id)} />
            ),
        },
        {
            field: 'leave_type_name',
            headerName: 'Type',
            width: 160,
            renderCell: (params) => <RenderCellBalanceType params={params} />,
        },
        {
            field: 'total_days',
            headerName: 'Total Days',
            width: 160,
            renderCell: (params) => <RenderCellTotalDays params={params} />,
        },
        {
            field: 'used_days',
            headerName: 'Used Days',
            width: 140,
            editable: true,
            renderCell: (params) => <RenderCellUsedDays params={params} />,
        },
        {
            field: 'remaining_days',
            headerName: 'Remaining Days',
            width: 110,
            type: 'singleSelect',
            editable: true,
            valueOptions: PUBLISH_OPTIONS,
            renderCell: (params) => <RenderCellRemainingDays params={params} />,
        },

    ];

    const getTogglableColumns = () =>
        columns
            .filter((column) => !HIDE_COLUMNS_TOGGLABLE.includes(column.field))
            .map((column) => column.field);


    return (
        <DashboardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
            <CustomBreadcrumbs
                heading="List"
                links={[
                    { name: 'Dashboard', href: paths.dashboard.root },
                    { name: 'Leave', href: paths.dashboard.leave.root },
                    { name: 'New leave application' },
                ]}
                sx={{ mb: { xs: 3, md: 5 } }}
            />

            <Card
                sx={{
                    minHeight: 640,
                    flexGrow: { md: 1 },
                    display: { md: 'flex' },
                    height: { xs: 800, md: '1px' },
                    flexDirection: { md: 'column' },
                }}
            >
                <DataGrid
                    checkboxSelection
                    disableRowSelectionOnClick
                    rows={tableData}
                    columns={columns}
                    loading={balancesLoading}
                    getRowHeight={() => 'auto'}
                    pageSizeOptions={[5, 10, 20, { value: -1, label: 'All' }]}
                    initialState={{ pagination: { paginationModel: { pageSize: 10 } } }}
                    onRowSelectionModelChange={(newSelectionModel) => setSelectedRowIds(newSelectionModel)}
                    columnVisibilityModel={columnVisibilityModel}
                    onColumnVisibilityModelChange={(newModel) => setColumnVisibilityModel(newModel)}
                    slots={{
                        noRowsOverlay: () => <EmptyContent />,
                        noResultsOverlay: () => <EmptyContent title="No results found" />,
                    }}
                    slotProps={{
                        toolbar: { setFilterButtonEl },
                        panel: { anchorEl: filterButtonEl },
                        columnsManagement: { getTogglableColumns },
                    }}
                    sx={{ [`& .${gridClasses.cell}`]: { alignItems: 'center', display: 'inline-flex' } }}
                />
            </Card>
        </DashboardContent>
    );
}

// ----------------------------------------------------------------------

declare module '@mui/x-data-grid' {
    interface ToolbarPropsOverrides {
        setFilterButtonEl: React.Dispatch<React.SetStateAction<HTMLButtonElement | null>>;
    }
}






