// İçe aktarma kontrolü: modül yüklenir, doğrulama API sembollerinin varlığı yazılır. Hiçbir işlev ÇAĞRILMAZ.
import * as m from 'jose';
console.log('modul=jose yuklendi; disa_aktarim_sayisi=' + Object.keys(m).length);
for (const s of ['jwtVerify', 'compactVerify', 'flattenedVerify', 'generalVerify', 'importJWK']) console.log('sembol', s, typeof m[s]);
