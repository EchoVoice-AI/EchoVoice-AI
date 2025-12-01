import type { AxiosRequestConfig } from 'axios';

import axios from 'axios';

import { CONFIG } from 'src/global-config';

// ----------------------------------------------------------------------

// Log configured server URL to help debug missing requests (remove in production)
if (typeof window !== 'undefined') {
  console.debug('[axios] CONFIG.serverUrl =', CONFIG.serverUrl || '(empty)');
}

const axiosInstance = axios.create({ baseURL: CONFIG.serverUrl });

axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject((error.response && error.response.data) || 'Something went wrong!')
);

export default axiosInstance;

// ----------------------------------------------------------------------

export const fetcher = async (args: string | [string, AxiosRequestConfig]) => {
  try {
    const [url, config] = Array.isArray(args) ? args : [args];

    const res = await axiosInstance.get(url, { ...config });

    return res.data;
  } catch (error) {
    console.error('Failed to fetch:', error);
    throw error;
  }
};

export const poster = async (args: string | [string, AxiosRequestConfig]) => {
  try {
    const [url, config] = Array.isArray(args) ? args : [args];

    const res = await axiosInstance.post(url, { ...config });

    return res.data;
  } catch (error) {
    console.error('Failed to post:', error);
    throw error;
  }
};

export const putter = async (args: string | [string, AxiosRequestConfig]) => {
  try {
    const [url, config] = Array.isArray(args) ? args : [args];

    const res = await axiosInstance.put(url, { ...config });

    return res.data;
  } catch (error) {
    console.error('Failed to put:', error);
    throw error;
  }
};

export const deleter = async (args: string | [string, AxiosRequestConfig]) => {
  try {
    const [url, config] = Array.isArray(args) ? args : [args];

    const res = await axiosInstance.delete(url, { ...config });

    return res.data;
  } catch (error) {
    console.error('Failed to delete:', error);
    throw error;
  }
};

// ----------------------------------------------------------------------

export const endpoints = {
  chat: '/api/chat',
  kanban: '/api/kanban',
  calendar: '/api/calendar',
  auth: { me: '/auth/me', signIn: '/auth/login', signUp: '/auth/register' },
  mail: { list: '/api/mail/list', details: '/api/mail/details', labels: '/api/mail/labels' },
  post: {
    list: '/api/post/list',
    details: '/api/post/details',
    latest: '/api/post/latest',
    search: '/api/post/search',
  },
  leave: {
    list: '/api/leave',
    details: '/api/leave/',
    search: '/api/leave/search',
    create: '/api/leave/create/',
    update: '/api/leave/update',
    delete: '/api/leave',
    balances: {
      list: '/api/leave/balances',
      details: '/api/leave/balances/',
      create: '/api/leave/balances/create/',
      update: '/api/leave/balances/update',
      delete: '/api/leave/balances',
    }
  },
  customer: {
    list: '/customers',
    details: '/customers/',
    search: '/customers/search',
    create: '/customers/create/',
    update: '/customers/',
    delete: '/customers',
  },
  package: {
    list: '/packages',
    details: '/packages/',
    search: '/packages/search',
    create: '/packages/create/',
    update: '/packages/update',
    delete: '/packages',
  },
  segmentor: {
    // Backend routes live under /api/segments
    list: '/segments',
    details: '/segments/',
    search: '/segments/search',
    create: '/segments/create/',
    update: '/segments/',
    delete: '/segments',
  },
};
