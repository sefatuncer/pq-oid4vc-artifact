// İçe aktarma kontrolü. Hiçbir işlev ÇAĞRILMAZ; çalışma/doğrulayıcı örneği oluşturulmaz.
const m = await import('@credo-ts/openid4vc');
const ad = Object.keys(m);
console.log('modul=@credo-ts/openid4vc yuklendi; disa_aktarim_sayisi=' + ad.length);
console.log('Verifier iceren semboller=' + ad.filter(a => /Verifier/.test(a)).sort().join(','));
