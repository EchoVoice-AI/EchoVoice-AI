import type { IDateValue, ISocialLink } from './common';

// ----------------------------------------------------------------------

export type IPackageProfileCover = {
  name: string;
  role: string;
  coverUrl: string;
  avatarUrl: string;
};

export type IPackageProfile = {
  id: string;
  role: string;
  quote: string;
  email: string;
  school: string;
  country: string;
  company: string;
  totalFollowers: number;
  totalFollowing: number;
  socialLinks: ISocialLink;
};

export type IPackageProfileFollower = {
  id: string;
  name: string;
  country: string;
  avatarUrl: string;
};

export type IPackageProfileGallery = {
  id: string;
  title: string;
  imageUrl: string;
  postedAt: IDateValue;
};

export type IPackageProfileFriend = {
  id: string;
  name: string;
  role: string;
  avatarUrl: string;
};

export type IPackageProfilePost = {
  id: string;
  media: string;
  message: string;
  createdAt: IDateValue;
  personLikes: { name: string; avatarUrl: string }[];
  comments: {
    id: string;
    message: string;
    createdAt: IDateValue;
    author: { id: string; name: string; avatarUrl: string };
  }[];
};

// Table Filters
export type IPackageTableFilters = {
  name: string;
  type: string[];
  status: string;
};

// Basic Voucher Card View
export type IVoucherCard = {
  id: string;
  name: string;
  type: string;
  status: string;
  price: number;
  validity_period: string;
  data_limit: string;
  rate_limit: string;
  subscribers: number;
};

// Full Voucher Item
export type IVoucherItem = {
  id: string;
  name: string;
  type: string;
  data_limit: string;
  time_limit: string;
  rate_limit: string;
  session_timeout: number;
  idle_timeout: number;
  price: number;
  status: string;
  validity_period: string;
  features: string;
  subscribers: number;
  description: string;
  created_at: IDateValue;
  updated_at: IDateValue;
};

// Package Billing/Subscription History
export type IPackageAccountBillingHistory = {
  id: string;
  packageId: string;
  userId: string;
  price: number;
  invoiceNumber: string;
  createdAt: IDateValue;
};
