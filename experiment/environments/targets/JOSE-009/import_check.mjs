// Import check: the module is loaded and the presence of the verification API symbols is written. NO function is called.
import * as m from 'jose';
console.log('modul=jose yuklendi; disa_aktarim_sayisi=' + Object.keys(m).length);
for (const s of ['jwtVerify', 'compactVerify', 'flattenedVerify', 'generalVerify', 'importJWK']) console.log('sembol', s, typeof m[s]);
