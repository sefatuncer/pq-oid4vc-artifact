// Bağlama (link) kontrolü: hedef JAR'daki bütün sınıflar İLKLENDİRİLMEDEN yüklenir (Class.forName(ad, false, ...)).
// Hiçbir yöntem çağrılmaz; imza doğrulama YOK. Çıkış 0 = anahtar sınıfların hepsi yüklendi.
import java.util.*;
import java.util.jar.*;
public class KontrolYukle {
    public static void main(String[] a) throws Exception {
        String jar = a[0];
        List<String> anahtar = Arrays.asList(a).subList(1, a.length);
        ClassLoader cl = KontrolYukle.class.getClassLoader();
        int ok = 0, hata = 0; Map<String, Integer> eksik = new TreeMap<>(); List<String> dogrulayici = new ArrayList<>();
        try (JarFile jf = new JarFile(jar)) {
            for (Enumeration<JarEntry> e = jf.entries(); e.hasMoreElements();) {
                String n = e.nextElement().getName();
                if (!n.endsWith(".class") || n.contains("module-info") || n.startsWith("META-INF/")) continue;
                String c = n.substring(0, n.length() - 6).replace('/', '.');
                if (c.substring(c.lastIndexOf('.') + 1).matches(".*(Verif|Validat).*") && !c.contains("$") && dogrulayici.size() < 25) dogrulayici.add(c);
                try { Class.forName(c, false, cl); ok++; }
                catch (Throwable t) { hata++; String m = String.valueOf(t.getMessage()); eksik.merge(t.getClass().getSimpleName() + ": " + m, 1, Integer::sum); }
            }
        }
        System.out.println("jar=" + jar.substring(jar.lastIndexOf('/') + 1) + " sinif_yuklendi=" + ok + " sinif_yuklenemedi=" + hata);
        eksik.entrySet().stream().limit(15).forEach(x -> System.out.println("  yuklenemedi: " + x.getKey() + " (x" + x.getValue() + ")"));
        System.out.println("ad_eslesen_siniflar (Verif|Validat; bilgi): " + String.join(",", dogrulayici));
        boolean tamam = true;
        for (String k : anahtar) {
            try { Class.forName(k, false, cl); System.out.println("anahtar_sinif " + k + " OK"); }
            catch (Throwable t) { tamam = false; System.out.println("anahtar_sinif " + k + " HATA " + t); }
        }
        System.exit(tamam ? 0 : 3);
    }
}
