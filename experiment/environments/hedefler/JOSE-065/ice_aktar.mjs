// İçe aktarma kontrolü (CJS paketi ESM'den). Hiçbir işlev ÇAĞRILMAZ.
import jwt from 'jsonwebtoken';
console.log('modul=jsonwebtoken yuklendi; anahtarlar=' + Object.keys(jwt).sort().join(','));
console.log('sembol verify', typeof jwt.verify);
