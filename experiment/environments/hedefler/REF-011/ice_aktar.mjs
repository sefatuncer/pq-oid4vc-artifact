// Import check. NO function is called; no instance/verifier object is created.
const m = await import('@credo-ts/openid4vc');
const ad = Object.keys(m);
console.log('modul=@credo-ts/openid4vc yuklendi; disa_aktarim_sayisi=' + ad.length);
console.log('Verifier iceren semboller=' + ad.filter(a => /Verifier/.test(a)).sort().join(','));
