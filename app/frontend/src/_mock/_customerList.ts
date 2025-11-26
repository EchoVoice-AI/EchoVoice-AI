
import { _mock } from './_mock';

export const _customerList = Array.from({ length: 20 }, (_, index) => ({
  id: _mock.id(index),
  username: _mock.username(index),
  zipCode: '85807',
  state: 'Virginia',
  city: 'Rancho Cordova',
  role: _mock.role(index),
  email: _mock.email(index),
  address: '908 Jack Locks',
  name: _mock.fullName(index),
  isVerified: _mock.boolean(index),
  service_type: index % 2 === 0 ? 'PPPoE' : 'Hotspot',
  country: _mock.countryNames(index),
  avatarUrl: _mock.image.avatar(index),
  phoneNumber: _mock.phoneNumber(index),
  status:
    (index % 2 && 'pending') || (index % 3 && 'banned') || (index % 4 && 'rejected') || 'active',
}));