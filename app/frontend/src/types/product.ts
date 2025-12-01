import type { IDateValue } from './common';

// ----------------------------------------------------------------------

export type IProductFilters = {
  rating: string;
  gender: string[];
  category: string;
  colors: string[];
  priceRange: number[];
};

export type IProductTableFilters = {
  stock: string[];
  publish: string[];
};

export type ILeaveTableFilters = {
  status: string[];
  leave_type: string[];
};

export type IProductReview = {
  id: string;
  name: string;
  rating: number;
  comment: string;
  helpful: number;
  avatarUrl: string;
  postedAt: IDateValue;
  isPurchased: boolean;
  attachments?: string[];
};

export type ILeaveItem = {
  id: string;
  leave_type: string;
  start_date: string | null;
  end_date: string | null;
  reason: string;
  status: string;
  applied_on: string;
  approved_by: string;
};

export type ILeaveItem2 = {
  id: string;
  leave_type: string;
  employee: string;
  start_date: string | null;
  end_date: string | null;
  leave_days: number;
  reason: string;
  status: string;
  applied_on: string;
  approved_by: string;
};

export type ILeaveBalance =
  {
    id: number;
    employee_name: string | null;
    leave_type_name: string | null;
    total_days: number,
    used_days: number,
    remaining_days: number
  }
