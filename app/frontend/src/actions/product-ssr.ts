import axios, { endpoints } from 'src/lib/axios';

// ----------------------------------------------------------------------

export async function getProducts() {
  const res = await axios.get(endpoints.leave.list);

  return res.data;
}

// ----------------------------------------------------------------------

export async function getProduct(id: string) {
  const URL = id ? `${endpoints.leave.details}?productId=${id}` : '';

  const res = await axios.get(URL);

  return res.data;
}
