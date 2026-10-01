// İçe aktarma kontrolü. Hiçbir işlev ÇAĞRILMAZ.
import * as m from '@sd-jwt/core';
console.log('modul=@sd-jwt/core yuklendi; disa_aktarim=' + Object.keys(m).sort().join(','));
console.log('sembol SDJwtInstance', typeof m.SDJwtInstance);
