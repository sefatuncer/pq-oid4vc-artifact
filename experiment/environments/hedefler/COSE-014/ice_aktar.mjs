// Import check. NO function is called.
import cose from 'cose-js';
console.log('modul=cose-js yuklendi; anahtarlar=' + Object.keys(cose).sort().join(','));
console.log('sembol sign.verify', typeof (cose.sign && cose.sign.verify));
