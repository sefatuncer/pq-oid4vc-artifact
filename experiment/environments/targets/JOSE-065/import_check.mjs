// Import check (CJS package from ESM). NO function is called.
import jwt from 'jsonwebtoken';
console.log('modul=jsonwebtoken yuklendi; anahtarlar=' + Object.keys(jwt).sort().join(','));
console.log('sembol verify', typeof jwt.verify);
